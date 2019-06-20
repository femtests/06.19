import time
import ssl
import os
from typing import Tuple, ContextManager
from io import BytesIO
from contextlib import contextmanager

import markdown
import certifi

from aiohttp import web, ClientSession, web_exceptions

sslcontext = ssl.create_default_context(cafile=certifi.where())

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):

    with open('README.md') as readme:
        return web.Response(
            body=markdown.markdown(readme.read()),
            content_type='text/html')


@routes.get('/timestamp')
async def get_current_time(request: web.Request):
    """ Get the time since the epoch. """
    return web.Response(text=str(int(time.time() * 1000)))


@contextmanager
def get_file(sha256sum: str) -> ContextManager[Tuple[BytesIO, int, str]]:
    """
    Uses a small map to get a IO object, iots size and its filename
    """
    mapping = {
        'cf5fab35c695388acd4bb6311629de66cf2707f32f6dd2557206c5f00318e3d8':
            'files/divina commedia.txt',
        '0841de1171babc79ec1928fe3e43db184b3b36c8dbddfbd5e66061ce1d639ddf':
            'files/moby dick.txt'
    }
    if sha256sum not in mapping:
        raise FileNotFoundError
    with open(mapping[sha256sum], mode='rb') as io:
        stat_info = os.stat(mapping[sha256sum])
        filename = os.path.split(mapping[sha256sum])[-1]
        yield io, stat_info.st_size, filename


@routes.get('/files/{id}')
async def get_file_bytes(request: web.Request):
    """
     Gets the file identified by the sha256sum.

     The client can decide the number of file to get using the
      "bytes" query param.

    """

    id = request.match_info['id']
    try:
        # all the following should probably go to another function
        with get_file(id) as (io, file_size, filename):

            # do we limit to N-nth byte or to the whole file?
            max_byte = request.query.get('max_byte', None)
            if max_byte:
                try:
                    max_byte = int(max_byte)
                except ValueError:
                    raise web_exceptions.HTTPBadRequest(
                        text=f'max_byte must be an integer "{max_byte}" found')
                if max_byte <= 0:
                    raise web_exceptions.HTTPBadRequest(
                        text=f'max_byte must be positive "{max_byte}" found')

            else:
                max_byte = file_size

            # We use a streaming response here
            response = web.StreamResponse(
                headers={
                    'Content-Length': str(max_byte),
                    'Content-Disposition': f'attachment;filename="{filename}"'
                })

            await response.prepare(request)

            # stream with 16 Kib chunks
            chunk_size = (2 ** 3) ** 4

            # Iterate  through the file until we hit 0.
            while max_byte > 0:
                chunk_size = min(max_byte, chunk_size)
                text = io.read(chunk_size)
                await response.write(text)
                max_byte -= chunk_size

            # ok we write the eof at the end of the cycle
            await response.write_eof(b'')

    except FileNotFoundError:
        raise web_exceptions.HTTPNotFound(text=f"Resource {id} not found.")
    return response


@routes.get('/proxy')
async def proxy_request(request: web.Request):
    """

    Before python3.7:
    For non ascii domains served under https,
    SSL handshake does not work properly.
    :param request:
    :return:
    """
    user_agent = 'Small Python Proxy'

    # we use the user agent to avoid the service proxing itself
    if request.headers.get('User-Agent') == user_agent:
        raise web_exceptions.HTTPNotImplemented(
            text=f'Proxy is not implemented for User-Agent: "{user_agent}".'
        )

    if not request.query_string.startswith('url='):
        raise web_exceptions.HTTPBadRequest(
            text='Missing querystring parameter `url`')
    else:
        # trim off the first 4 characters [url=] from the querystring
        url = request.query_string[4:]

        content_type, text = await request_page(url, user_agent)

        response = web.Response(
            content_type=content_type,
            text=text
        )
        return response


async def request_page(url: str, user_agent: str) -> Tuple[str, str]:
    """
    Request a page with the GET HTTP method and return the status code
     and it content-type
    """
    async with ClientSession(
            headers={'User-Agent': user_agent}) as client:
        proxied = await client.get(
            url=url,
            ssl=sslcontext,
        )
        content_type = proxied.content_type
        text = await proxied.text()
        return content_type, text

app = web.Application()
app.add_routes(routes)

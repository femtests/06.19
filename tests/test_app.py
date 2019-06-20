import time
from unittest import mock
from datetime import date, timedelta
import pytest

from aiohttp import web
from app import routes


@pytest.fixture
async def client(aiohttp_client, loop):
    app = web.Application()
    app.router.add_routes(routes)
    client = await aiohttp_client(app)
    return client


async def test_timestamp(client):
    """
    Test that the given timestamp

    """
    start = int(time.time() * 1000)

    resp = await client.get('/timestamp')
    timestamp = await resp.text()

    end = int(time.time() * 1000)

    msg = f'{timestamp} expected to be within {start} and {end}'
    assert start <= int(timestamp) <= end, msg
    expected = date(1970, 1, 1)
    actual = date.today() - timedelta(milliseconds=int(timestamp))
    assert expected == actual, f'{expected} is not 1st January 1970!'


@pytest.fixture
async def mock_request_page():
    async def mocked(ur, user_agent):
        return 'text/simple', 'test body'
    with mock.patch('app.request_page', new=mocked) as mocked:
        yield mocked


class TestProxyRequest:
    async def test_proxy_request(self, client, mock_request_page):
        """
        Is the first time I try aiohttp,
        I have no idea how to mock the client at the moment.
        """
        response = await client.get('/proxy?url=https://test.com?test=true')
        response_text = await response.text()
        assert response_text == 'test body'

    async def test_bad_request(self, client):
        """
        Test when we don't use the url parameter at the beginning of the
         query string
        """
        response = await client.get(
            '/proxy?a=1&url=https://test.com?test=true')
        response_text = await response.text()
        assert response.status == 400
        assert response_text == 'Missing querystring parameter `url`'

    @pytest.mark.skip(msg='Not implemented')
    async def test_invalid_agent(self, client):
        """
        Test when we don't use the agent is not valid
        """
        NotImplemented


class GetFileBytes:
    @pytest.mark.skip(msg='not impemetned')
    def test_whole_file(self):
        NotImplemented

    @pytest.mark.skip(msg='not impemetned')
    def test_file_part(self):
        NotImplemented

    @pytest.mark.skip(msg='not impemetned')
    def test_not_found(self):
        NotImplemented

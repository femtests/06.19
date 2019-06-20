Hello!
======

THe server does not really have an interface, except this readme.

Let's try that I took the opportunity to try out the
 [AIOHTTP](https://aiohttp.readthedocs.io/en/stable/)
 library.


the server is a bare minimum and I didn't reallly finish with the unittest.

Entry points
============

### `/timestamp`
Returns the Unix TImestamp since the epch in milliseconds

Example: http://0.0.0.0:9990/timestamp
### `/files/{id}[?[max_bytes={number of bytes: positive integer}]]`


Streams a file if the id is known of, 
Example: http://0.0.0.0:9990/files/0841de1171babc79ec1928fe3e43db184b3b36c8dbddfbd5e66061ce1d639ddf

#### Optional query parameters:
- max_bytes: Number of bytes of the file to return.


### `/proxy?url={url: string}`
Request the webpage and returns it with.

Example: http://0.0.0.0:9990/proxy?url=https://example.com

Deployment
=========

To deploy you can either use your host machine or Docker.

### Host machine
1. Create A virtual environment and run `pip intall -r requirements.txt`.
2. Run `gunicorn app:app --bind 0.0.0.0:9090 --worker-class aiohttp.GunicornWebWorker`
3. The webserver should be listening to the url `http://0.0.0.0:9090`


### Docker
The easiest way is to use the docker-compose file and run 
```docker-compose up --build```
you should be ablle to visit this url: http://0.0.0.0:9990

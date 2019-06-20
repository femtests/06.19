FROM python:3.7 as base

WORKDIR app

ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

ADD . .


# running the tests.
FROM base as test

RUN flake8 .

RUN pytest tests


# main image
FROM base as main
ENV PORT=8090
CMD gunicorn app:app --bind 0.0.0.0:${PORT} --worker-class aiohttp.GunicornWebWorker

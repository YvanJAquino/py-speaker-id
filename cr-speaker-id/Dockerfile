FROM    python:3.9-buster AS base
ENV     PYTHONUNBUFFERED True
WORKDIR /src
RUN     apt update && \
        pip install pipenv

FROM    base
COPY    *.py Pipfile* ./
ADD     modules/* modules/

RUN     pipenv install --system --deploy
CMD     gunicorn --bind 0.0.0.0:$PORT -w 4 -k uvicorn.workers.UvicornWorker main:app 
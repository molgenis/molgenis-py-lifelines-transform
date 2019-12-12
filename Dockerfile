# vim:set ft=dockerfile:
FROM python:3.8-slim-buster
WORKDIR /root/lifelines-transform

COPY ./poetry.lock /root/lifelines-transform
COPY ./pyproject.toml /root/lifelines-transform

RUN pip install poetry &&\
 poetry install -n --no-dev

COPY . /root/lifelines-transform

CMD [ "poetry", "run", "python", "src/main.py"]
FROM molgenis/docker-poetry:latest
WORKDIR /usr/src/app
ENV POETRY_CACHE_DIR /usr/src/app/.cache

COPY . /usr/src/app
RUN poetry update

CMD [ "poetry", "run", "python", "lifelines_transform/main.py"]
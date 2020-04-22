FROM molgenis/docker-poetry:latest
WORKDIR /usr/src/app
ENV POETRY_CACHE_DIR /usr/src/app/.cache

COPY ./pyproject.toml /usr/src/app
COPY . /usr/src/app
RUN poetry install -n --no-dev

CMD [ "poetry", "run", "python", "lifelines_transform/main.py"]
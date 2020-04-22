FROM molgenis/docker-poetry:latest
WORKDIR /root/lifelines-transform

COPY ./poetry.lock /root/lifelines-transform
COPY ./pyproject.toml /root/lifelines-transform
COPY . /root/lifelines-transform
RUN poetry install -n --no-dev

CMD [ "poetry", "run", "python", "lifelines_transform/main.py"]
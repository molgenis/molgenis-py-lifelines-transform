# vim:set ft=dockerfile:
FROM archlinux

RUN echo Server = http://ftp.nluug.nl/os/Linux/distr/archlinux/\$repo/os/\$arch > /etc/pacman.d/mirrorlist
RUN pacman -Sy --noconfirm
RUN pacman -S python-pip --noconfirm

WORKDIR /root/lifelines-transform

COPY ./poetry.lock /root/lifelines-transform
COPY ./pyproject.toml /root/lifelines-transform

RUN pip install poetry &&\
 poetry install -n --no-dev

COPY . /root/lifelines-transform

CMD [ "poetry", "run", "python", "src/main.py"]
# vim:set ft=dockerfile:
FROM archlinux

RUN echo Server = http://ftp.nluug.nl/os/Linux/distr/archlinux/\$repo/os/\$arch > /etc/pacman.d/mirrorlist
RUN pacman -Syu --noconfirm
RUN pacman -S git openssh python-pip --noconfirm

COPY . /root/lifelines-transform
WORKDIR /root/lifelines-transform

RUN pip install poetry &&\
 poetry install -n --no-dev

CMD [ "poetry", "run", "python", "src/main.py"]
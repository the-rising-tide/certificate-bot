ARG ARCH=
FROM ${ARCH}ubuntu:20.04

COPY ./site.yml /root/.ansible/site.yml

RUN apt update && \
    apt install -y ansible aptitude python3-apt && \
    ansible-playbook /root/.ansible/site.yml && \
    apt-get remove -y --purge ansible python3-apt && \
    apt-get autoremove -y && \
    apt-get autoclean && \
    apt-get clean

VOLUME /app/
WORKDIR /app

COPY src/ /app/

CMD groupadd python -g ${GID:-1000} && \
    useradd -u ${UID:-1000} -g ${GID:-1000} python && \
    chown -R  python:python /app && \
    su python -c '/venvs/venv/bin/python3 main.py'

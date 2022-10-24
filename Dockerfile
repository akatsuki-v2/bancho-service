FROM python:3.10

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install -U pip setuptools
RUN pip install -r requirements.txt

COPY scripts /scripts
RUN chmod u+x /scripts/*

COPY mount /srv/root
WORKDIR /srv/root

EXPOSE 80

CMD ["/scripts/bootstrap.sh"]

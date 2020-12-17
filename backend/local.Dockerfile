FROM python:3.7.3

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential \
    libcurl4-openssl-dev \
    libjpeg-dev \
    libgif-dev \
    libffi-dev \
    libpng-dev \
    libtiff-dev \
    libxml2-dev \
    libxslt-dev \
    xmlsec1 \
    vim \
    ntp \
    git-core \
    python-dev \
    python-setuptools \
    postgresql-client \
    libpq-dev \
    python-psycopg2 \
    python-gdal \
    gdal-bin \
    libgdal-dev \
    libgdal20

RUN pip install --upgrade pip

WORKDIR /tmp

RUN pip install "poetry==1.1.4"
ADD pyproject.toml poetry.lock /tmp/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

ADD . /code/

WORKDIR /code/

EXPOSE 8000

RUN wget -O /code/psql-cert.crt https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem

ADD ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]

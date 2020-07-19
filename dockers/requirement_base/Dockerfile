FROM python:3
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install zip unzip -y
COPY ./requirements/base.txt .
RUN pip install --upgrade pip
RUN pip install -r base.txt
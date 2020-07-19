FROM mopitz/requirements_base:latest
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install zip unzip -y
RUN mkdir /code
WORKDIR /code
COPY ./ /code/
ENV DJANGO_SETTINGS_MODULE=economic_system.settings.jupyter_dev
RUN pip install --upgrade pip
RUN pip install -r requirements/dev.txt
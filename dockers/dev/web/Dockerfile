FROM mopitz/requirements_base:latest
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install zip unzip -y    
WORKDIR /code
COPY ./requirements/base.txt ./
COPY ./requirements/dev.txt ./
RUN pip install --upgrade pip
RUN pip install -r dev.txt
COPY ./ ./
ENV DJANGO_SETTINGS_MODULE=economic_system.settings.dev
ENV ENVIRONMENT=dev

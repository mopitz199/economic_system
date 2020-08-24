FROM mopitz/requirements_base:latest
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY ./ /code/
ENV DJANGO_SETTINGS_MODULE=economic_system.settings.jupyter_prod
ENV ENVIRONMENT=prod
RUN pip install --upgrade pip
RUN pip install -r requirements/prod.txt
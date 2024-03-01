FROM python:slim

WORKDIR /root/rishat_stripe/

COPY ${REPO_DIR} $WORKDIR

RUN pip3 install -r requirements.txt
RUN python manage.py migrate --settings=config.settings.docker_dev

EXPOSE 8000


CMD gunicorn --bind :8000 --workers 3 config.wsgi_docker_dev:application
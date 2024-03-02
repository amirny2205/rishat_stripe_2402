FROM python:slim
ENV DJANGO_SETTINGS_MODULE=config.settings.docker_dev
ENV WSGI_MODULE=config.wsgi_docker_dev
WORKDIR /root/rishat_stripe/
COPY ${REPO_DIR} $WORKDIR
RUN pip3 install -r requirements.txt
EXPOSE 8000
CMD python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE; python manage.py collectstatic --noinput --settings=$DJANGO_SETTINGS_MODULE; gunicorn --bind :8000 --workers 3 $WSGI_MODULE:application
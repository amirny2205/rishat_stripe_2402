from .base import *

ALLOWED_HOSTS = ['backend', '192.168.2.172', 'localhost', '127.0.0.1']

environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env_docker_compose'))

SECRET_KEY = env("SECRET_KEY")
STRIPE_API_KEY = env("STRIPE_API_KEY")
STRIPE_SECRET_API_KEY = env("STRIPE_SECRET_API_KEY")


# при разработке может быть полезна команда
# docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my-postgres
# которая выдаст ip-адрес postgres контейнера

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "rishat_db",
        'USER': env("DATABASE_USER"),
        'PASSWORD': env("DATABASE_PASSWORD"),
        'HOST': 'db',
        'PORT': 5432,
   }
}

from .base import *

ALLOWED_HOSTS = ['backend', 'localhost', '127.0.0.1']
[ALLOWED_HOSTS.append(host) for host in json.loads(os.getenv('ALLOWED_HOSTS'))]
[CSRF_TRUSTED_ORIGINS.append('http://' + origin) for origin in ALLOWED_HOSTS]
[CSRF_TRUSTED_ORIGINS.append('https://' + origin) for origin in ALLOWED_HOSTS]
DEBUG = os.getenv('DEBUG', 'False') == 'True'


environ.Env.read_env(env_file=os.path.join(BASE_DIR, '.env_docker_compose'))

SECRET_KEY = env("SECRET_KEY")
STRIPE_API_KEY = env("STRIPE_API_KEY")
STRIPE_SECRET_API_KEY = env("STRIPE_SECRET_API_KEY")

CHECKOUT_RETURN_URL = env("CHECKOUT_RETURN_URL", 
                          default="http://localhost:8000/payment_submitted/")

# при разработке может быть полезна команда
# docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my-postgres
# которая выдаст ip-адрес postgres контейнера,
# который можно указать как хост, и текущий докер сможет до него достучаться

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env("POSTGRES_DB"),
        'USER': env("POSTGRES_USER"),
        'PASSWORD': env("POSTGRES_PASSWORD"),
        'HOST': env("POSTGRES_HOST"),
        'PORT': env("POSTGRES_PORT")
   }
}

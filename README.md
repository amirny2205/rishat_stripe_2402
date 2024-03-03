### Описание сервиса
Сервис представляет собой выполнение вот этого [тестого задания](https://docs.google.com/document/d/1fEjqKUwsPOXPLeeFJL8GqKzfC755Ancnu1y1zQbBA4o/edit?usp=sharing)


Сервис используется в https://github.com/amirny2205/rishat_stripe_2402_compose , там его можно запустить, предоставив только `.env_docker_compose` файл и заполнив базу, можно использовать вот эту [фикстуру](https://drive.google.com/file/d/1KQT0axvxT2Njr_FVmOaOwsrOhReLy4jT/view?usp=drive_link). В фикстуре есть админ: имя `admin` пароль `q`. Админка доступна по пути `admin/`. Локально фикстура подгружается командой `./manage.py loaddata fixture_240229.json`


Доступные эндпоинты:
- _items/_  
  основная страница, с которой начинает пользователь. Там можно выбрать товары, активировать промокоды для получения скидки, перейти на страницу оплаты _checkout/_
- _checkout/_  
  страница оплаты. После оплаты пользователя перенаправляет на страицу _payment_submitted/_, на которой виден статус платежа. 
- _payment_submitted/_  
  пользователя перенаправляет на эту страницу с _checkout/_, она показывает статус платежа, с неё можно вернуться обратно на _items/_
- _buy/_  
  на этот эндпоинт отправляет запрос скрипт со страницы _checkout/_, здесь создаётся payment_intent, создаётся объект order, пока еще неподтвержеднный. Подтверждается он через вебхук _webhook/_ , слушающий сервис stripe-cli, который описан чуть дальше.
- _check_promocode/_  
  на этот эндпоинт отправляется запрос со страницы _items/_ чтобы проверить, доступен ли промокод для активации
- _webhook/_  
  вебхук слушает сервис stripe-cli, который описан чуть дальше и меняет статус соответствующих order на complete
- _admin/_  
  стандартная джанговская админская панель


### Общие требования
- Запущенная postgres с созданной rishat_db. Креденшиалс (POSTGRES_USER, POSTGRES_PASSWORD) прописываются в `.env*`

- Запущенный сервис stripe-cli. Без них сервис работает, только объекты order не будут подтверждены. Если вы не запускаете продакшен-версию сервиса, этот пункт можно пропустить.  
  Запуск показан на https://docs.stripe.com/stripe-cli  
  Нам нужно слушать сообщения о статусе платежей:  
  `stripe listen --forward-to localhost:8000/webhook/ --api-key sk_test_`  
  Через докер может быть удобнее:  
  `docker run --rm --network=host -dit stripe/stripe-cli listen --forward-to localhost:8000/webhook/ --api-key sk_test_`

### Запуск сервиса без docker
1. Создать `.env` файл: `cp ./.env_example .env`  
   Заполнить его соответственно. Ключи страйп получать на их сайте, в своем дешборде   
   `ALLOWED_HOSTS` автоматически добавляются к уже имеющемуся списку (`['localhost', '127.0.0.1']`)  
   В `config/settings/base.py` при необходимости заменить переменную `CHECKOUT_RETURN_URL` - это абсолютный путь к странице с _payment_submit/_, его использует скрипт stripe на странице _checkout/_ . Заменить, когда ваш итоговый хостнейм будет отличаться  
2. создаём виртуальную среду: `python3 -m venv venv`
3. активируем её, на линуксе это: `source ./venv/bin/activate`
4. устанавливаем зависимости: `pip install -r requirements.txt`
5. проводим миграции: `./manage.py migrate`
6. по желанию, подгружаем фикстуру(ы). Можете воспользоваться той, ссылка на которую дана в начале этого readme
7. запускаем сервис: `./manage.py runserver`

Теперь на `localhost:8000/items/` браузер должен показывать страницу с выбором вещей

### Запуск сервиса с docker
Напоминаю, что по умолчанию докер контейнер не имеет доступа к сети хоста, поэтому, чтобы использовать postgres, одним из решений будет `docker run --network host ...`

Запуск сервиса:
1. cоздать `.env_docker_dev` файл: `cp ./.env_example .env_docker_dev`  
   Заполнить его соответственно.  
   `ALLOWED_HOSTS` автоматически добавляются к уже имеющемуся списку (`['localhost', '127.0.0.1']`)
2. сбилдить образ: `docker build -f django.Dockerfile -t rishat_django .`
3. запустить образ: `docker run -dit --env-file .env_docker_dev -e POSTGRES_DB=rishat_db -e POSTGRES_HOST=172.17.0.3 -e POSTGRES_PORT=5432 -e CHECKOUT_RETURN_URL=http://localhost:8000/payment_submitted/ -p 8000:8000 rishat_django`  
  `POSTGRES_HOST` здесь ведёт к докеру с postgres, его ip можно получить командой `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' my-postgres`  
  `CHECKOUT_RETURN_URL` - это абсолютный путь к странице с _payment_submit/_, его использует скрипт stripe на странице _checkout/_ . Заменить, когда ваш итоговый хостнейм будет отличаться.

Теперь на `localhost:8000/items/` браузер должен показывать страницу с выбором вещей

Сервис по умолчанию запускает gunicorn, тот не сервирует статику, и, чтобы не развалилось то, что от неё зависит, например админская панель, необходимо после запуска докера (он делает `collectstatic`) скопировать статику в соответствующее место, откуда она будет сервироваться (напр. через nginx). Для этого можно использовать `docker cp ...`, папка со статикой должна сервироваться по адресу _static/_ или, в случае с docker-compose, можно посмотреть как это сделано у меня: https://github.com/amirny2205/rishat_stripe_2402_compose  

### Сервис nginx
можно использовать сервис nginx, созданный в процессе решения этой задачи: https://github.com/amirny2205/rishat_stripe_2402_nginx

команда копирования статики выглядит так: 
```
docker cp 2d46:/root/rishat_stripe/static .
docker cp ./static/* 2122:/home/nginx_user/rishat_nginx/django_static/
```

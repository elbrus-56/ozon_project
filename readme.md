# Ozon DRF

## Установка
git clone 
python3 -m venv venv
source venv/bin/activate
cd ozondrf
pip install -r requirements.txt

## Команды
`
python manage.py makemigrations
python manage.py migrate 
python manage.py createsuperuser 

`
## Основные функции
#### Обработка новых заказов
`python manage.py process_orders `

#### Получение наклеек
`python manage.py get_pdf_labels `

#### Получение актов
`python manage.py get_acts `

#### Уведомления о arbitration
`python manage.py process_arbitration [--email] [--telegram]`

#### Уведомления о client arbitration
`python manage.py process_client_arbitration [--email] [--telegram] `

#### Уведомления о cancelled
`python manage.py process_cancelled [--email] [--telegram] `

#### Очистка файлов
`python manage.py cleanup_files [--days=30] `


```
## Celery
* run worker
`celery -A ozondrf worker -E  -l debug`
* run celery-beat
`celery -A ozondrf beat -l info`
* Конфигурация запуска (crontab) - ozondrf/celery.py

## Особенности реализации
* ozon_manager.py - функции взаимодействия с API Ozon (класс OzonManager)
* tusmk.py - функции взаимодействия с ТУС МС (класс TusMK)
* helpers.py - вспомогательные функции  - отправка уведомлений и документов в Телеграм, email, проверка помещаемости в упаковку
*   

#### Тесты основных функций
```cd ozondrf
   python connector/test.py
```
#### Запуск
source venv/bin/activate
cd ozondrf
# в 3х разных окнах
gunicorn --bind 127.0.0.1:8050 ozondrf.wsgi
python -m celery -A ozondrf beat
python -m celery -A ozondrf worker

### Супервизор
sudo apt-get install -y supervisor
не используется

### Виртуальное окружение
в каталоге ozon-drf-main
создаём виртуальное окружение.
python3 -m venv venv

### Docker Compose
важно в ubuntu сделать -
Step 1. Open /etc/sysctl.conf file.
sudo nano /etc/sysctl.conf
Step 2. Update or add the following line at the end of the file.
vm.overcommit_memory = 1
## запуск
sudo docker-compose down -v && sudo docker-compose up -d
## мягкая остновка
sudo docker-compose down -v
## логи
sudo docker-compose logs

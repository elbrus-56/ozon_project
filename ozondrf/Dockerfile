FROM python:3.8.5

WORKDIR /app/ozondrf
RUN pip install --upgrade pip setuptools wheel

# Обновляем пакетный менеджер
RUN apt-get update -y && apt-get upgrade -y

# Ставим зависимости GDAL, PROJ
RUN apt-get install -y gdal-bin libgdal-dev
RUN apt-get install -y python3-gdal
RUN apt-get install -y binutils libproj-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./bin/start_gunicorn.sh
RUN chmod +x bin/start_celery.sh

CMD ["sh", "./bin/start_gunicorn.sh"]
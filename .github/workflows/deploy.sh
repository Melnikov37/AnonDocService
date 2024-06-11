#!/bin/bash

# Путь до директории, где расположено ваше приложение на сервере
APP_DIR=~/app

# Переходим в директорию приложения
cd $APP_DIR

# Получаем последнюю версию кода из репозитория
git pull origin main

# Активация виртуального окружения
source env/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r project/requirements.txt
pip install --force git+https://github.com/pydantic/pydantic.git@464ed49b1f813103a49116476bec75a94492b338
python -m spacy download ru_core_news_sm

# Перезапуск сервиса
# Предполагается, что вы используете systemd для управления вашим сервисом
python project/app.py

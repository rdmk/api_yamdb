## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```Shell
git clone https://github.com/BadBedBatPenguin/api_yamdb.git
```

```Shell
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```Shell
python3 -m venv env
```

```Shell
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```Shell
python3 -m pip install --upgrade pip
```

```Shell
pip install -r requirements.txt
```

Выполнить миграции:

```Shell
python3 manage.py migrate
```

Запустить проект:

```Shell
python3 manage.py runserver
```

## Использованные технологии

Django\
Django rest framework\
SimpleJWT

## Наполнение базы данных из csv файлов
поместить все необходимые csv файлы в диекторию "api_yamdb/static/data/" \
выполнить команду:

```Shell
python3 manage.py import_csv
```

## Авторы

Бахмутов Алексей ([Patron322] (https://github.com/Patron322)) \
Мункуев Эрдэм ([rdmk] (https://github.com/rdmk)) \
Цёсь Максим ([BadBedBatPenguin] (https://github.com/BadBedBatPenguin))

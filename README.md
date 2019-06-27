# niffler-backend 后台部署文档

- django rest framework 3.9.2
- python 3.5-3.7

[![Build Status](https://travis-ci.org/sysu-swsad-team/niffler-backend.svg?branch=master)](https://travis-ci.org/sysu-swsad-team/niffler-backend)

## Install

```bash
git clone https://github.com/sysu-swsad-team/niffler-backend.git
cd niffler/
pip install -r requirements.txt
```

## Reset the database

```bash
python manage.py flush
```

## Run

```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/questionnaire/，成功则返回 {}

## API Docs

Open http://127.0.0.1:8000/questionnaire/swagger/

## Admin Site

create a superuser account of admin site so as to manage the data model 

```bash
python manage.py createsuperuser 
```

Open http://127.0.0.1:8000/admin/

## Unit Test

```bash
python manage.py test
```

## Reference

https://docs.djangoproject.com/zh-hans/2.2/

http://www.iamnancy.top/djangorestframework/Home/

## Project Structure

```bash
niffler
    ├── avatar
    │   └── 1.jpg
    ├── db.sqlite3
    ├── log.txt
    ├── manage.py
    ├── niffler
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── questionnaire
    │   ├── Untitled.ipynb
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── migrations
    │   │   ├── 0001_initial.py
    │   │   ├── 0002_auto_20190625_0042.py
    │   │   ├── 0003_auto_20190625_0305.py
    │   │   ├── __init__.py
    │   ├── models.py
    │   ├── serializers.py
    │   ├── swagger_schema.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    └── requirements.txt
```


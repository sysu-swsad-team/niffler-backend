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
Open http://127.0.0.1:8000/questionnaire/

## API Docs

Open http://127.0.0.1:8000/questionnaire/swagger/

## Admin Site

创建超级用户并进入 admin 界面管理某个数据模型

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


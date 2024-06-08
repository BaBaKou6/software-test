A simple project build with Django



cd project 

python manage.py makemigrations app

python manage.py migrate


python manage.py runserver

regist project route in project/urls.py

```
http://127.0.0.1:8000/api/test/     
```
regist api route in project/app/urls.py

```
http://127.0.0.1:8000/api/task/create-or-update
```

 CSRF when request api in postman

api
1. get user info
2. create-or-update task 


user

user_credit

user_score

task  phase

task_step  task_id step_id status


A simple project build with Django



Register our app in Django framework `project/settings.py`
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',  // add our app to this line
]
```

Usage:
```
cd project 
<!-- create superuser -->
python manage.py createsuperuser
```
superuser
admin
admin
```
<!-- when you create a new model or update a model's field, make migrate -->
python manage.py makemigrations app

python manage.py migrate

<!-- run server -->
python manage.py runserver
```
Regist project route in `project/urls.py`
```
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("app.urls")), // add our api route to project
]
```

Regist API route in `project/app/urls.py`
```
urlpatterns = [    
    path("task/create-or-update", views.task, name="create-or-update-task"),    
]
```
API url
```
http://127.0.0.1:8000/api/task/create-or-update
```


## API 文档

### 任务创建或更新接口

**URL**: `/api/task/create-or-update`

**方法**: `POST`

**描述**: 该接口用于创建或更新任务。只有管理员用户可以访问此接口。

### 请求头

- `Content-Type: application/json`

### 请求参数

**类型**: `JSON`

| 参数名     | 类型   | 必填 | 描述                          |
|------------|--------|------|-------------------------------|
| stage      | String | 是   | 任务的阶段                    |
| score      | Integer| 是   | 任务的分数                    |
| task_id    | Integer| 否   | 要更新的任务ID（如果是更新）  |
| name       | String | 否   | 任务名称（如果是创建新任务）  |

### 请求示例

**创建任务**:

```json
{
  "stage": "init",
  "score": 50,
  "name": "New Task"
}
```

**更新任务**:

```json
{
  "stage": "finished",
  "score": 50,
  "task_id": 1
}
```

### 响应参数

**类型**: `JSON`

| 参数名    | 类型   | 描述                      |
|-----------|--------|---------------------------|
| status    | Integer| 响应状态码                |
| data      | Object | 详细数据或消息            |
| msg       | String | 响应消息                  |

### 响应示例

**成功响应**:

```json
{
  "status": 200,
  "data": "success",
  "msg": ""
}
```

**错误响应**:

```json
{
  "status": 403,
  "data": {},
  "msg": "user does not have permission"
}
```

### 错误代码

| 状态码    | 描述                               |
|-----------|------------------------------------|
| 200       | 请求成功                           |
| 400       | 请求无效，JSON解析错误或缺少参数   |
| 403       | 权限不足，用户没有执行该操作的权限 |
| 404       | 用户或任务未找到                   |
| 405       | 方法不允许，应该使用POST请求       |

### 备注

- 该接口要求用户必须是管理员组成员，才能创建或更新任务。
- 在创建任务时，用户的分数必须足够，否则会返回403错误。
- 在更新任务时，只有存在的任务才能被更新，否则会返回404错误。


from urllib import request
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from app.models import Task, User
import json

def init_group(request):
    try:
        user = request.user
        print(user)
        data = {
            'project': 'test',
            'api': 'api',    
        }   
        
        from django.contrib.auth.models import User, Group
        
        
        # Create groups for different roles
        admin_group = Group.objects.get(name='admin')
        if not admin_group:
            Group.objects.create(name='admin')
            
        user_group = Group.objects.get(name='user')
        if not user_group:
            Group.objects.create(name='user')        

        # Assign users to groups
        user = User.objects.get(username='admin')        

        user.groups.add(user_group)
        user.groups.add(admin_group)  # for admin users
   
        
       
    except Exception as e:
        print(e)
    
    return JsonResponse({"status": 200, "data": data})

# Create your views here.
def index(request):
    try:
        user = request.user
        print(user)
        data = {
            'project': 'test',
            'api': 'api',    
        }   
        
        u = User(username='api_test', age=28, gender='M', 
                 birthday='1990-12-12', email='api@test.com',
                 credit = 10000,
                 score= 9999999,
                 level=1)
        u.save()
    except Exception as e:
        print(e)
    
    
    return JsonResponse({"status": 200, "data": data})


# http://127.0.0.1:8000/api/task/create-or-update
@csrf_exempt
def task(request):
    # API7 为了防止异常追踪和其他有价值的信息被传回攻击者，如果可以，定义和强制使用统一的API响应格式，包括错误信息；
    # 统一返回格式json {"status": 405, "data": {}, "msg": "method not allowed"}
    
    if request.method != 'POST':
        # API7 确定API只能被特定HTTP方法访问，其他的HTTP方法访问都应该被禁止（如，POST方法）
        return JsonResponse({"status": 405, "data": {}, "msg": "method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "data": {}, "msg": "invalid JSON"}, status=400)

    # logined_in user
    user = request.user
    
    # API5 失效的功能级授权 检查用户是否有权限执行此操作
    # 显式授予特定角色才能访问这个功能；admin 才能访问
    if not user.groups.filter(name='admin').exists():
        return JsonResponse({"status": 403, "data": {}, "msg": "user does not have permission"}, status=403)

    
    
    task_id = data.get('task_id', 0)
    
    try:
        # app user
        app_user = User.objects.get(username=user.username)
    except User.DoesNotExist:
        return JsonResponse({"status": 404, "data": {}, "msg": "user not found"}, status=404)
    
    user_id = app_user.id
    stage = data.get("stage")
    score = data.get("score")
    
    print(stage)
    if stage is None or score is None:
        return JsonResponse({"status": 400, "data": {}, "msg": "missing stage or score"}, status=400)
    
    # API 6  仅将客户端可更新的属性列入白名单；
    # API 8  对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理
    if not Task.TaskStage.validStage(stage):
        return JsonResponse({"status": 400, "data": {}, "msg": "invalid stage"}, status=400)
    # API 6  仅将客户端可更新的属性列入白名单；
    # API 8  对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理
    if score < 0:
        return JsonResponse({"status": 400, "data": {}, "msg": "invalid score"}, status=400)
    
    try:
        task = Task.objects.get(id=task_id)
        # Update a exites task
        if task:
            # API 6  仅将客户端可更新的属性列入白名单；
            task.stage = stage
            
            if stage == Task.TaskStage.finished:
                app_user.credit += score
                app_user.save()
            task.save()
    except Task.DoesNotExist:
        # Check user's score before creating a new task
        # API 6  仅将客户端可更新的属性列入白名单；
        # API 8  对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理
        if app_user.score < score:
            return JsonResponse({"status": 403, "data": {}, "msg": "user doesn't have enough score"}, status=403)
        
        # Create a new task within a transaction
        with transaction.atomic():
            app_user.score -= score
            app_user.save()

            task = Task(
                name=data.get("name", ""),
                user_id=user_id,
                stage=stage,
                score=score
            )
            task.save()
    
    return JsonResponse({"status": 200, "data": "success"})
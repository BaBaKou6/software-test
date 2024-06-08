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
    if request.method != 'POST':
        return JsonResponse({"status": 405, "data": {}, "msg": "method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "data": {}, "msg": "invalid JSON"}, status=400)

    user = request.user
    
    # API5 失效的功能级授权 检查用户是否有权限执行此操作
    # 显式授予特定角色才能访问这个功能；admin 才能访问
    if not user.groups.filter(name='admin').exists():
        return JsonResponse({"status": 403, "data": {}, "msg": "user does not have permission"}, status=403)

    
    user_id = data.get('user_id')
    task_id = data.get('task_id', 0)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"status": 404, "data": {}, "msg": "user not found"}, status=404)
   
    stage = data.get("stage")
    score = data.get("score")
    
    if stage is None or score is None:
        return JsonResponse({"status": 400, "data": {}, "msg": "missing stage or score"}, status=400)
    
    try:
        task = Task.objects.get(id=task_id)
        # Update task
        if task:
            task.stage = stage
            
            if stage == Task.TaskStage.finished:
                user.credit += score
                user.save()
            task.save()
    except Task.DoesNotExist:
        # Check user's score before creating a new task
        if user.score < score:
            return JsonResponse({"status": 403, "data": {}, "msg": "user not enough score"}, status=403)
        
        # Create a new task within a transaction
        with transaction.atomic():
            user.score -= score
            user.save()

            task = Task(
                name=data.get("name", ""),
                user_id=user_id,
                stage=stage,
                score=score
            )
            task.save()
    
    return JsonResponse({"status": 200, "data": "success"})
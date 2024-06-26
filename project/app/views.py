from urllib import request
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from app.models import Task, User
import json

# 初始化用户组
def init_group(request):
    try:
        login_user = request.user
        print(login_user.username)
        data = {
            'project': 'test',
            'api': 'api',    
        }   
        
        from django.contrib.auth.models import User as Auth_User, Group
        
        api_group_role = "api_role"
        
        # Create groups for different roles
        auth_group = Group.objects.get_or_create(name=api_group_role)[0]        
        user_group = Group.objects.get_or_create(name='user')[0]          
        
        # Assign users to groups
        auth_user = Auth_User.objects.get(username=login_user.username)        
        
        auth_user.groups.add(user_group)
        auth_user.groups.add(auth_group)  # for auth users

        u = User(username=login_user.username, age=28, gender='M', 
                 birthday='1990-12-12', email='api@test.com',
                 credit = 10000,
                 score= 9999999,
                 level=1)
        u.save()
        
        print(u)
        
       
    except Exception as e:
        print(e)
    
    return JsonResponse({"status": 200, "data": data})

# Create your views here.
# 用于测试
def index(request):
    try:
        user = request.user
        print(user)
        data = {
            'project': 'test',
            'api': 'api',    
        }   
        
        u = User(username='root', age=28, gender='M', 
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
    # API采用统一格式返回
    # {"status": 405, "data": {}, "msg": "method not allowed"}
    
    # 只接受POST请求，非POST请求拒绝访问
    if request.method != 'POST':
        # API7 确定API只能被特定HTTP方法访问，其他的HTTP方法访问都应该被禁止（如，POST方法）
        return JsonResponse({"status": 405, "data": {}, "msg": "method not allowed"}, status=405)
    
    try:
        # 从HTTP的Body中解析json请求数据对象
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "data": {}, "msg": "invalid JSON"}, status=400)

    # 获取当前登录用户，对于授权，你可以换成token或其他的监权方式
    user = request.user
    
    # API5 失效的功能级授权 检查用户是否有权限执行此操作
    # 显式授予特定角色才能访问这个功能；admin 才能访问
    if not user.groups.filter(name='admin').exists():
        return JsonResponse({"status": 403, "data": {}, "msg": "user does not have permission"}, status=403)

    
    # API8 注入 对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理；
    task_id = data.get('task_id', 0)
    
    try:
        # 根据登录用户，去获取我们app对应的任务用户
        app_user = User.objects.get(username=user.username)
    except User.DoesNotExist:
        return JsonResponse({"status": 404, "data": {}, "msg": "user not found"}, status=404)
    
    user_id = app_user.id
    # 前端请求的信息，用于创建或更新task
    stage = data.get("stage")
    score = data.get("score")
    
    # API8 注入 对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理；
    if stage is None or score is None:
        return JsonResponse({"status": 400, "data": {}, "msg": "missing stage or score"}, status=400)
    
    # API 6  仅将客户端可更新的属性列入白名单；
    # API 8  对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理
    if not Task.TaskStage.validStage(stage):
        return JsonResponse({"status": 400, "data": {}, "msg": "invalid stage"}, status=400)
    # API 6  仅将客户端可更新的属性列入白名单；
    # API 8  对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理
    if score < 0:
        # score必须是大于0的数值，不然前端传负值，会对业务数据造成不可预料的影响
        return JsonResponse({"status": 400, "data": {}, "msg": "invalid score"}, status=400)
    
    try:
        # 根据前端传的task_id去判断，是创建新task，还是更新已有的task
        task = Task.objects.get(id=task_id)        
        if task:
            # 更新已有的task
            # API 6  仅将客户端可更新的属性列入白名单；
            task.stage = stage
            
            # 如果是完成task，则给该用户增加相应的积分
            if stage == Task.TaskStage.finished:
                app_user.credit += score
                app_user.save()
            task.save()
    except Task.DoesNotExist:
        if task_id:
            return JsonResponse({"status": 403, "data": {}, "msg": "task doesn't exists"}, status=403)
        
        # Check user's score before creating a new task
        # API 6  仅将客户端可更新的属性列入白名单；
        # API 8  对客户端提供的数据、或其他来自集成系统的数据进行验证、过滤和清理
        if app_user.score < score:
            # 这是我们设计的业务逻辑，创建新任务时，消耗用户一定的分数。如果用户的分数不足，则无法创建。
            return JsonResponse({"status": 403, "data": {}, "msg": "user doesn't have enough score"}, status=403)
        
        # Create a new task within a transaction
        with transaction.atomic():
            # 在事务的原子操作里，对用户的分数进行扣除，并创建一个新任务。
            app_user.score -= score
            app_user.save()

            # 创建一个新task
            task = Task(
                name=data.get("name", ""),
                user_id=user_id,
                stage=stage,
                score=score
            )
            task.save()
    
    return JsonResponse({"status": 200, "data": "success"})
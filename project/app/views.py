from django.shortcuts import render
from django.http import JsonResponse

from app.models import Task, User
import json



# Create your views here.
def index(request):
    
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
    
    
    return JsonResponse({"status": 200, "data": data})

# http://127.0.0.1:8000/api/task/create-or-update
def task(request):
    if request.method == 'POST':
        data = json.loads(request.body) # parse the JSON data into a dictionary
    else:
        return JsonResponse({"status": 200, "data": {}, "msg": "method not supported"})
       
    user_id, task_id  = data['user_id'], data.get('task_id', 0)
    try:
        user = User.objects.get(id=user_id)
        if not user:
            return JsonResponse({"status": 200, "data": {}, "msg": "user not found"})
    except Exception as e:
        return JsonResponse({"status": 200, "data": {}, "msg": "user not found"})
   
    stage, score = data["stage"], data["score"]
    try:
        task = Task.objects.get(id=task_id)
        # udpate
        if task:
            task.stage = stage
            
            if stage == Task.TaskStage.finished:
                user.credit += score
                user.save()
            task.save()
            
    except Exception as e:
                
        if user.score < score:
            return JsonResponse({"status": 200, "data": {}, "msg": "user not enough score"})
        
        # user need score to create a task, if the user doesn't have enough score, return an error        
        # need transaction here
        user.score -= score
        user.save()
        
        
        task = Task(
            name=data["name"], 
            user_id=data["user_id"],
            stage=data["stage"],
            score=data["score"]
        )
        task.save()    
      
       
    
    
    return JsonResponse({"status": 200, "data": "sucess"})
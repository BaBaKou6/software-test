from django.shortcuts import render
from django.http import JsonResponse

from app.models import Task
import json



# Create your views here.
def index(request):
    
    data = {
        'project': 'test',
        'api': 'api',    
    }   
    
    
    
    return JsonResponse({"status": 200, "data": data})

# http://127.0.0.1:8000/api/task/create-or-update
def task(request):
    
    if request.method == 'POST':
        data = json.loads(request.body) # parse the JSON data into a dictionary
    
    
    task = Task(
        name=data["name"], 
        user_id=data["user_id"],
        stage=data["stage"],
        score=data["score"]
    )
    ret = task.save()
    
    return JsonResponse({"status": 200, "data": ret})
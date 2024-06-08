from random import choice
from django.db import models

# Create your models here.

class User(models.Model):
    class Sex(models.TextChoices):
        M = "male"
        F = "female"
        
    
    username = models.CharField(max_length=32)
    age = models.IntegerField()
    gender = models.CharField(max_length=32, choices=Sex)
    birthday = models.DateField()
    email = models.EmailField()
    
    credit = models.IntegerField()
    score = models.IntegerField()
    level = models.IntegerField()
    
    created = models.DateField(auto_now=True)
    last_modified = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
        
        
class Task(models.Model):
    class TaskStage(models.TextChoices):
        init = "male"
        doing = "female"
        finished = "finished"
        cancelled = "cancelled"
        
    name = models.CharField(max_length=64)
    user_id = models.IntegerField()
    stage = models.CharField(max_length = 32, choices=TaskStage)
    score = models.IntegerField()
    
      
    created = models.DateField(auto_now=True)
    last_modified = models.DateField(auto_now=True)
    
    class Meta:
        verbose_name = "任务"
        verbose_name_plural = "任务"
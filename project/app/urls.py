from django.urls import path

from . import views

urlpatterns = [
    path("test/", views.index, name="index"),
    path("task/create-or-update", views.task, name="create-or-update-task"),
    
    
]
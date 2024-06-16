from django.urls import path

from . import views

urlpatterns = [
    path("test/", views.index, name="index"),
    path("init_group", views.init_group, name="init_group"),
    path("task/create-or-update", views.task, name="create-or-update-task"),    
]
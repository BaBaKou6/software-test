from django.contrib import admin
from app.models import User, Task
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("username", )
    list_display = ("username", "age", "gender", "birthday", "email", "credit", "score", "level", "created")
    
    
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ("name", )
    list_display = ("name", "user_id", "stage", "score", "created")
    
    
from django.urls import path
from .views import (
    signup_view, login_view, logout_view,
    todo_page_view, task_list_api, toggle_task_api, delete_task_api
)

urlpatterns = [
    # Pages
    path('', todo_page_view, name='home'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Task APIs
    path('api/tasks/', task_list_api, name='task_list_api'),
    path('api/tasks/<int:task_id>/toggle/', toggle_task_api, name='toggle_task_api'),
    path('api/tasks/<int:task_id>/delete/', delete_task_api, name='delete_task_api'),
]
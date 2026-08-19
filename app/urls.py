from django.urls import path
from . import views

urlpatterns = [
    # Existing UI & APIs...
    path('login/', views.login_page_view, name='login'),
    path('signup/', views.signup_page_view, name='signup'),
    path('forgot-password/', views.forgot_password_page_view, name='forgot_password'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_page_view, name='password_reset_confirm'),
    path('', views.todo_page_view, name='home'),
    path('logout/', views.logout_view, name='logout'),

    path('api/signup/', views.signup_api, name='api_signup'),
    path('api/login/', views.login_api, name='api_login'),
    path('api/tasks/', views.task_list_api, name='api_tasks'),
    path('api/tasks/<int:task_id>/toggle/', views.toggle_task_api, name='api_toggle_task'),
    path('api/tasks/<int:task_id>/delete/', views.delete_task_api, name='api_delete_task'),
    
    # Password Reset API endpoints
    path('api/password-reset/', views.password_reset_request_api, name='api_password_reset'),
    path('password-reset/done/', views.password_reset_done_page_view, name='password_reset_done'),
    path('api/password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_api, name='api_password_reset_confirm'),
]
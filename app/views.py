import json
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from .models import Task

def signup_view(request):
    # 1. Render the HTML page when user opens the link in browser
    if request.method == 'GET':
        return render(request, 'sign_up.html')

    # 2. Process sign-up when JavaScript submits data
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')

            # Validation checks
            if not all([username, email, password, confirm_password]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)

            if password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match.'}, status=400)

            if len(password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters long.'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username is already taken.'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email is already registered.'}, status=400)

            # Create User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            return JsonResponse({'message': 'Account created successfully!'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            password = data.get('password', '')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required.'}, status=400)

            # Authenticate verifies the hashed password against the DB
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # login creates the session cookie in the user's browser
                login(request, user)
                return JsonResponse({'message': 'Login successful!'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)

@login_required(login_url='/login/')
def todo_page_view(request):
    return render(request, 'Todo_Page.html')


# --- API ENDPOINTS ---
@login_required(login_url='/login/')
def task_list_api(request):
    """GET: Fetch all tasks | POST: Create a task"""
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user)
        task_data = [
            {'id': t.id, 'title': t.title, 'completed': t.completed} 
            for t in tasks
        ]
        return JsonResponse({'tasks': task_data})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '').strip()
            if not title:
                return JsonResponse({'error': 'Task title cannot be empty.'}, status=400)

            task = Task.objects.create(user=request.user, title=title)
            return JsonResponse({'id': task.id, 'title': task.title, 'completed': task.completed}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required(login_url='/login/')
@require_POST
def toggle_task_api(request, task_id):
    """Toggle completion status"""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.completed = not task.completed
        task.save()
        return JsonResponse({'id': task.id, 'completed': task.completed})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)


@login_required(login_url='/login/')
@require_POST
def delete_task_api(request, task_id):
    """Delete a task"""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.delete()
        return JsonResponse({'message': 'Task deleted'})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)


def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('/login/')
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from .models import Task
from .serializers import TaskSerializer, RegisterSerializer


def logout_view(request):
    """Clears the session cookie and redirects to login"""
    logout(request)
    return redirect('/login/')


# ==========================================
# 1. HTML TEMPLATE VIEWS (For rendering UI)
# ==========================================

def login_page_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'login.html')

def signup_page_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'sign_up.html')

def todo_page_view(request):
    return render(request, 'Todo_Page.html')

def forgot_password_page_view(request):
    """Renders the HTML page for entering the email address"""
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'app/password_reset.html')

def password_reset_confirm_page_view(request, uidb64, token):
    """Renders the HTML page for entering a new password"""
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'app/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})

def password_reset_done_page_view(request):
    """Renders the confirmation page after an email reset has been requested"""
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'app/password_reset_done.html')


# ==========================================
# 2. DRF API ENDPOINTS (Uses Session Auth)
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def signup_api(request):
    """Handles registration via JS fetch()"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Account created successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny]) 
def login_api(request):
    """Handles login via JS fetch() and sets the session cookie"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return Response({'message': 'Login successful!'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_api(request):
    """GET: Fetch user tasks | POST: Create task"""
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response({'tasks': serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def toggle_task_api(request, task_id):
    """Toggle completion status"""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    task.completed = not task.completed
    task.save()
    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def delete_task_api(request, task_id):
    """Delete a task"""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    task.delete()
    return Response({'message': 'Task deleted successfully'}, status=status.HTTP_200_OK)


# ==========================================
# 3. PASSWORD RESET API ENDPOINTS
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_api(request):
    """Handles password reset request via JS fetch() and sends fully customized email"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host() or '127.0.0.1:8000'
        
        context = {
            'user': user,
            'protocol': protocol,
            'domain': domain,
            'uid': uid,
            'token': token,
        }
        
        # Point directly to your unique template path to prevent Django default template collision
        html_content = render_to_string('registration/email_password_reset.html', context)
        
        text_content = (
            f"Hello {user.username},\n\n"
            f"We received a request to reset your password for your Task-Flow account.\n"
            f"Please go to the following page to choose a new password:\n\n"
            f"{protocol}://{domain}/reset/{uid}/{token}/\n\n"
            f"If you didn't request this, you can safely ignore this email.\n\n"
            f"The Task-Flow Team"
        )
        
        subject = "Reset Your Task-Flow Password"
        email_msg = EmailMultiAlternatives(subject, text_content, None, [user.email])
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

    except User.DoesNotExist:
        pass

    return Response(
        {'message': 'If an account with this email exists, a password reset link has been sent.'}, 
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_api(request, uidb64, token):
    """Handles updating the password using the token sent in the reset link"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({'error': 'Both password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        form = SetPasswordForm(user, {'new_password1': new_password, 'new_password2': confirm_password})
        if form.is_valid():
            form.save()
            return Response({'message': 'Password has been reset successfully! You can now log in.'}, status=status.HTTP_200_OK)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'The reset link is invalid or has expired.'}, status=status.HTTP_400_BAD_REQUEST)
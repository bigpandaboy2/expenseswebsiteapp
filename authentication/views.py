import json
import threading
from django.shortcuts import redirect, render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


class UsernameValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse(
                {'username_error': 'Username should only contain alphanumeric characters.'},
                status=400
            )
        
        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {'username_error': 'Choose another username since it is already taken.'},
                status=409
            )
        
        return JsonResponse({'username_valid': True})
    

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        context = {
            "fieldValues": request.POST
        }

        if not username or not email or not password:
            messages.error(request, "Please fill in all the fields.")
            return render(request, 'authentication/register.html', context)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'authentication/register.html', context)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return render(request, 'authentication/register.html', context)
        
        if len(password) < 6:
            messages.error(request, "Password too short. Minimum 6 characters.")
            return render(request, 'authentication/register.html', context)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.is_active = True
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        domain = get_current_site(request).domain
        link = reverse(
            'activate', 
            kwargs={
                    'uidb64': uidb64, 
                    'token': token_generator.make_token(user),
            }
        )

        activate_url = f"http://{domain}{link}"

        email_subject = 'Activate your account'
        email_body = 'Hi ' + user.username + '!\n' \
                    'Please use this link to verify your account:\n' + activate_url
        email = EmailMessage(
            email_subject,
            email_body,
            'noreply@semycolon.com',
            [email],
        )
        EmailThread(email).start()

        messages.success(request, "Account successfully created!")  
        return render(request, 'authentication/register.html')
    

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse(
                {'email_error': 'Email is invalid.'},
                status=400
            )
        
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {'email_error': 'Choose another email since it is already taken.'},
                status=409
            )
        
        return JsonResponse({'email_valid': True})
    

class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if user.is_active:
                messages.info(request, "Account already activated.")
                return redirect('login')

            if token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                messages.success(request, 'Account activated successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Activation link is invalid or has expired.')
                return redirect('login')

        except Exception as e:
            messages.error(request, 'Something went wrong during activation.')
            return redirect('login')
    

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' + user.username + '! You are now logged in!')
                    return redirect('expenses')

                messages.error(request, 'Account is not active, please check your email.')
                return render(request, 'authentication/login.html')
            
            messages.error(request, 'Invalid credentials, please try again.')
            return render(request, 'authentication/login.html')
        
        messages.error(request, 'Please fill all the fields.')
        return render(request, 'authentication/login.html')
    

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('login')
    

class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST.get('email')
        context = {'values': request.POST}

        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please supply a valid email.')
            return render(request, 'authentication/reset-password.html', context)

        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            user = user_qs.first()
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            domain = get_current_site(request).domain
            reset_link = reverse('reset-user-password', kwargs={
                'uidb64': uidb64,
                'token': token,
            })
            activate_url = f"http://{domain}{reset_link}"

            email_subject = 'Reset Your Password'
            email_body = f"Hi {user.username},\n\nUse this link to reset your password:\n{activate_url}"

            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@semycolon.com',
                [email]
            )

            EmailThread(email).start()

            messages.success(request, "We've sent you an email to reset your password.")
            return render(request, 'authentication/reset-password.html')

        messages.error(request, 'No user is associated with this email.')
        return render(request, 'authentication/reset-password.html', context)

    

class CompletePasswordReset(View):
    def get(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid, please request a new one.')
                return render(request, 'authentication/reset-password.html')

        except Exception as e:
            pass

        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'Password too short. Minimum 6 characters.')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successfully. You can now log in with your new password.')
            return redirect('login')

        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
            return render(request, 'authentication/set-new-password.html', context)
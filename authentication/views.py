from django.shortcuts import redirect, render
from django.views import View
import json
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
        user.is_active = False
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
        email.send(fail_silently=False)

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
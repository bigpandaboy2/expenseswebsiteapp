from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages

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
        user.save()

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
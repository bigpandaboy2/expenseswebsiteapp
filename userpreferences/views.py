import os
import json
from django.shortcuts import render
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='/authentication/login')
def index(request):
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    user_preferences = UserPreference.objects.filter(user=request.user).first()

    if request.method == 'POST':
        currency = request.POST.get('currency')
        if user_preferences:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)

        messages.success(request, 'Changes saved.')

    return render(
        request,
        'preferences/index.html',
        {
            'currencies': currency_data,
            'user_preferences': user_preferences,
        }
    )
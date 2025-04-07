from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from userpreferences.models import UserPreference
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except UserPreference.DoesNotExist:
        currency = 'USD'

    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        category = request.POST.get('category')
        date = request.POST.get('expense_date')

        if not amount or not description or not category or not date:
            messages.error(request, 'All fields are required.')
            return render(request, 'expenses/add_expense.html', {
             'categories': categories,
                'values': request.POST
            })

        Expense.objects.create(
            amount=amount,
            description=description,
            category=category,
            date=date,
            owner=request.user
        )

        messages.success(request, 'Expense added successfully.')
        return redirect('expenses')
    

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit-expense.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required.')
            return render(request, 'expenses/edit-expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'Description is required.')
            return render(request, 'expenses/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense. date = date
        expense.category = category
        expense.description = description

        expense.save()
        messages.success(request, 'Expense updated  successfully!')

        return redirect('expenses')
    

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed.')
    return redirect('expenses')


@login_required(login_url='/authentication/login')
def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=180)

    expenses = Expense.objects.filter(
        owner=request.user, 
        date__gte=six_months_ago, 
        date__lte=todays_date  
    )

    final_report = {}

    categories = expenses.values_list('category', flat=True).distinct()

    for category in categories:
        total_amount = sum(exp.amount for exp in expenses.filter(category=category))
        final_report[category] = float(total_amount)

    return JsonResponse({'expense_category_data': final_report}, safe=False)

@login_required(login_url='/authentication/login')
def stats_view(request):
    return render(request, 'expenses/stats.html')


@login_required(login_url='/authentication/login')
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses_' + \
        str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([
            expense.amount,
            expense.description,
            expense.category,
            expense.date
        ])

    return response


@login_required(login_url='/authentication/login')
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses_' + \
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')

    row_num = 0

    header_style = xlwt.XFStyle()
    header_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], header_style)

    data_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'category', 'date'
    )

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), data_style)

    wb.save(response)
    return response


@login_required(login_url='/authentication/login')
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Expenses_' + \
        datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary' 

    expenses = Expense.objects.filter(owner=request.user)
    total = expenses.aggregate(Sum('amount'))

    html_string = render_to_string(
        'expenses/pdf-output.html', 
        {'expenses': expenses, 'total': total['amount__sum']}
    )

    html = HTML(string=html_string)

    with tempfile.NamedTemporaryFile(delete=True) as output:
        html.write_pdf(target=output.name)
        output.flush()

        with open(output.name, 'rb') as f:
            response.write(f.read())

    return response
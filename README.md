# 💸 Personal Finance Manager

A web application to track your personal income and expenses. Built with Django, Bootstrap, and Chart.js, this app allows you to categorize, analyze, and visualize your financial data.

---

## 🚀 Features

- ✅ User registration & login
- 🔒 Password reset via email
- 💰 Add / edit / delete income and expenses
- 📊 Categorize entries and track spending
- 🔍 Real-time search functionality (AJAX-based)
- ⚙️ User preference for currency selection
- 📈 Interactive data visualization using Chart.js
- 🐳 Docker support for easy deployment

---

## 🧰 Tech Stack

- Python 3.11+
- Django 5.1.7
- Bootstrap 5
- JavaScript / Chart.js
- SQLite (default) or PostgreSQL
- Docker + Pipenv

---
## Environment Variables
Check ".env.example" and apply to your environemnt:

- SECRET_KEY=your_django_secret_key
- DEBUG=True
- EMAIL_HOST=smtp.example.com
- EMAIL_PORT=587
- EMAIL_HOST_USER=your_email@example.com
- EMAIL_HOST_PASSWORD=your_password
- EMAIL_USE_TLS=True

## 📦 Installation

### 🔧 Prerequisites

- Python 3.11+
- Pipenv
- Docker (optional)

### 💻 Local Setup

```bash
# Clone the repo
git clone https://github.com/bigpandaboy2/expenseswebsiteapp.git
cd expenseswebsite

# Install dependencies
pipenv install

# Activate the virtual environment
pipenv shell

# Apply migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver
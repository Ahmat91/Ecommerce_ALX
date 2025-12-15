🛒 NexusStore E-commerce Product API

This repository contains the backend API for a simple e-commerce platform, built as the final Capstone Project. The API provides robust CRUD functionality for product management, user authentication, searching, and filtering, leveraging Django and Django REST Framework (DRF).

✨ Key Features

Product CRUD: Full functionality to Create, Read, Update, and Delete products.

Authentication: Secured endpoints using DRF's Token Authentication.

Authorization: Custom permission (IsAdminOrReadOnly) ensures only staff users can modify product data.

Search & Filtering: Products can be searched by name and description and filtered by Category, Price Range, and Stock availability.

Pagination: Results for product listings and search queries are paginated for performance.

Admin Panel: Customized Django Admin for easy data management and custom stock actions.

💻 Tech Stack

Backend: Python 

Web Framework: Django 

API Framework: Django REST Framework (DRF)

Database: SQLite (Development) / PostgreSQL (Production ready)

🚀 Setup and Running Locally

Follow these steps to get the project running on your local machine.

Prerequisites

Python 

pip (Python package installer)

Installation

Clone the Repository:

git clone [Your Public GitHub Repository URL]
cd api_project


Create and Activate Virtual Environment:

# Create environment
python -m venv venv
# Activate environment (Windows)
.\venv\Scripts\activate
# Activate environment (macOS/Linux)
source venv/bin/activate


Install Dependencies:

pip install -r requirements.txt 
# NOTE: You will need to create a requirements.txt file with:
# Django
# djangorestframework
# django-filter
# djangorestframework-simplejwt (if you switched from TokenAuth)


Database Setup:

# Create database tables based on models
python manage.py makemigrations api
python manage.py migrate


Create Admin User:

# Required to access the Admin panel and create products
python manage.py createsuperuser


Run the Server:

python manage.py runserver

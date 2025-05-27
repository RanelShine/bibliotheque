import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from catalogue.models import Book, Author, Category, Loan

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )

@pytest.fixture
def category():
    return Category.objects.create(
        name='Roman',
        description='Romans littéraires'
    )

@pytest.fixture
def author():
    return Author.objects.create(
        first_name='Victor',
        last_name='Hugo',
        biography='Écrivain français du XIXe siècle',
        birth_date='1802-02-26'
    )

@pytest.fixture
def book(category, author):
    book = Book.objects.create(
        title='Les Misérables',
        isbn='9780140444308',
        category=category,
        summary='L\'histoire de Jean Valjean',
        total_copies=3,
        available_copies=2,
        publication_date='1862-01-01'
    )
    book.authors.add(author)
    return book

@pytest.fixture
def loan(book, user):
    return Loan.objects.create(
        book=book,
        borrower=user,
        loan_date=timezone.now(),
        return_due_date=timezone.now() + timedelta(days=14),
        status='B'
    ) 
import pytest
from django.contrib.auth.models import User
from catalogue.models import Author, Book, Category, Loan
from django.utils import timezone
from datetime import timedelta

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )

@pytest.fixture
def category():
    return Category.objects.create(
        name='Fiction',
        description='Fiction books'
    )

@pytest.fixture
def author():
    return Author.objects.create(
        first_name='Victor',
        last_name='Hugo',
        biography='French novelist',
        birth_date='1802-02-26'
    )

@pytest.fixture
def book(category, author):
    book = Book.objects.create(
        title='Les Misérables',
        isbn='9781234567890',
        category=category,
        summary='French historical novel',
        total_copies=3,
        available_copies=3,
        publication_date='1862-01-01'
    )
    book.authors.add(author)
    return book

@pytest.fixture
def loan(book, user):
    loan_date = timezone.now()
    return_due_date = loan_date + timedelta(days=14)
    return Loan.objects.create(
        book=book,
        borrower=user,
        loan_date=loan_date,
        return_due_date=return_due_date,
        status='B'
    ) 
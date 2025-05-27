import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from catalogue.models import Book, Author, Category, Loan

@pytest.mark.django_db
class TestCategoryAPI:
    def test_category_list(self, client, category):
        """Test retrieving category list."""
        url = reverse('category-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == category.name

    def test_category_detail(self, client, category):
        """Test retrieving category detail."""
        url = reverse('category-detail', kwargs={'pk': category.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name

@pytest.mark.django_db
class TestAuthorAPI:
    def test_author_list(self, client, author):
        """Test retrieving author list."""
        url = reverse('author-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['last_name'] == author.last_name

    def test_author_detail(self, client, author):
        """Test retrieving author detail."""
        url = reverse('author-detail', kwargs={'pk': author.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['last_name'] == author.last_name

@pytest.mark.django_db
class TestBookAPI:
    def test_book_list(self, client, book):
        """Test retrieving book list."""
        url = reverse('book-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == book.title

    def test_book_detail(self, client, book):
        """Test retrieving book detail."""
        url = reverse('book-detail', kwargs={'pk': book.pk})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == book.title

    def test_book_create(self, admin_user, category, author):
        """Test creating a book through API."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        url = reverse('book-list')
        data = {
            'title': 'New Book',
            'isbn': '9780123456789',
            'author_ids': [author.id],
            'category_id': category.id,
            'total_copies': 1,
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.filter(title='New Book').exists()

    def test_book_reserve(self, client, book, user):
        """Test reserving a book."""
        client.force_authenticate(user=user)
        url = reverse('book-reserve', kwargs={'pk': book.pk})
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.available_copies == book.total_copies - 1

@pytest.mark.django_db
class TestLoanAPI:
    def test_loan_list(self, client, admin_user, loan):
        """Test retrieving loan list."""
        client.force_authenticate(user=admin_user)
        url = reverse('loan-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_loan_create(self, client, admin_user, book, user):
        """Test creating a loan through API."""
        client.force_authenticate(user=admin_user)
        url = reverse('loan-list')
        data = {
            'book_id': book.id,
            'borrower': user.id,
            'return_due_date': '2024-12-31T23:59:59Z'
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Loan.objects.filter(book=book, borrower=user).exists()

    def test_return_book(self, client, admin_user, loan):
        """Test returning a book through API."""
        client.force_authenticate(user=admin_user)
        url = reverse('loan-return-book', kwargs={'pk': loan.pk})
        initial_copies = loan.book.available_copies
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        loan.refresh_from_db()
        assert loan.return_date is not None
        loan.book.refresh_from_db()
        assert loan.book.available_copies == initial_copies + 1

@pytest.mark.django_db
class TestAPIPermissions:
    """Test API permissions."""

    def test_unauthenticated_read_access(self, client, book):
        """Test that unauthenticated users can read public data."""
        urls = [
            reverse('book-list'),
            reverse('author-list'),
            reverse('category-list'),
        ]
        for url in urls:
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_write_access(self, client, category):
        """Test that unauthenticated users cannot write data."""
        urls = [
            (reverse('book-list'), {'title': 'Test Book', 'isbn': '9780123456789'}),
            (reverse('author-list'), {'first_name': 'Test', 'last_name': 'Author'}),
            (reverse('category-list'), {'name': 'Test Category'}),
        ]
        for url, data in urls:
            response = client.post(url, data, format='json')
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_loan_access_restricted(self, client, loan):
        """Test that loan data is restricted to authenticated users."""
        url = reverse('loan-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 
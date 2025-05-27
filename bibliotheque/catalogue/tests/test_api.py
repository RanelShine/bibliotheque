import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from catalogue.models import Book, Author, Category, Loan
from catalogue.serializers import BookSerializer, AuthorSerializer, CategorySerializer, LoanSerializer

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.mark.django_db
class TestBookAPI:
    def test_book_list(self, authenticated_client, book):
        """Test getting book list."""
        url = reverse('catalogue:book-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == book.title

    def test_book_detail(self, authenticated_client, book):
        """Test getting book detail."""
        url = reverse('catalogue:book-detail', kwargs={'pk': book.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == book.title

    def test_book_create(self, authenticated_client, category, author):
        """Test creating a book."""
        url = reverse('catalogue:book-list')
        data = {
            'title': 'New Book',
            'isbn': '9780123456789',
            'authors': [author.id],
            'category': category.id,
            'total_copies': 1,
            'available_copies': 1,
            'summary': 'Test book'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.filter(title='New Book').exists()

    def test_book_update(self, authenticated_client, book):
        """Test updating a book."""
        url = reverse('catalogue:book-detail', kwargs={'pk': book.pk})
        data = {
            'title': 'Updated Title',
            'isbn': book.isbn,
            'authors': [author.id for author in book.authors.all()],
            'category': book.category.id,
            'total_copies': book.total_copies,
            'available_copies': book.available_copies,
            'summary': book.summary
        }
        response = authenticated_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert book.title == 'Updated Title'

    def test_book_delete(self, authenticated_client, book):
        """Test deleting a book."""
        url = reverse('catalogue:book-detail', kwargs={'pk': book.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(pk=book.pk).exists()

@pytest.mark.django_db
class TestAuthorAPI:
    def test_author_list(self, authenticated_client, author):
        """Test getting author list."""
        url = reverse('catalogue:author-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['last_name'] == author.last_name

    def test_author_detail(self, authenticated_client, author):
        """Test getting author detail."""
        url = reverse('catalogue:author-detail', kwargs={'pk': author.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['last_name'] == author.last_name

    def test_author_create(self, authenticated_client):
        """Test creating an author."""
        url = reverse('catalogue:author-list')
        data = {
            'first_name': 'Jules',
            'last_name': 'Verne',
            'birth_date': '1828-02-08',
            'biography': 'French novelist'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.filter(last_name='Verne').exists()

@pytest.mark.django_db
class TestCategoryAPI:
    def test_category_list(self, authenticated_client, category):
        """Test getting category list."""
        url = reverse('catalogue:category-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == category.name

    def test_category_create(self, authenticated_client):
        """Test creating a category."""
        url = reverse('catalogue:category-list')
        data = {
            'name': 'Science Fiction',
            'description': 'Science fiction books'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='Science Fiction').exists()

@pytest.mark.django_db
class TestLoanAPI:
    def test_loan_list(self, authenticated_client, loan):
        """Test getting loan list."""
        url = reverse('catalogue:loan-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_loan_create(self, authenticated_client, book, user):
        """Test creating a loan."""
        url = reverse('catalogue:loan-list')
        data = {
            'book': book.id,
            'borrower': user.id,
            'return_due_date': '2024-12-31T23:59:59Z',
            'status': 'B'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Loan.objects.filter(book=book, borrower=user).exists()

    def test_loan_return(self, authenticated_client, loan):
        """Test returning a loan."""
        url = reverse('catalogue:loan-detail', kwargs={'pk': loan.pk})
        data = {
            'return_date': '2024-01-01T12:00:00Z',
            'status': 'C'
        }
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        loan.refresh_from_db()
        assert loan.status == 'C'

@pytest.mark.django_db
class TestAPIAuthentication:
    """Test API authentication requirements."""
    
    def test_unauthenticated_access(self, api_client):
        """Test that unauthenticated access is denied."""
        urls = [
            reverse('catalogue:book-list'),
            reverse('catalogue:author-list'),
            reverse('catalogue:category-list'),
            reverse('catalogue:loan-list'),
        ]
        
        for url in urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED 
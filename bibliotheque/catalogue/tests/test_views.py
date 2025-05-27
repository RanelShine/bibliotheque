import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from catalogue.models import Book, Author, Category, Loan

@pytest.mark.django_db
class TestBookViews:
    def test_book_list_view(self, client, book):
        """Test the book list view."""
        url = reverse('book_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'books' in response.context
        assert list(response.context['books']) == [book]

    def test_book_search(self, client, book):
        """Test the book search functionality."""
        url = reverse('book_list')
        response = client.get(url, {'query': 'Misérables'})
        assert response.status_code == 200
        assert list(response.context['books']) == [book]

        # Test search with no results
        response = client.get(url, {'query': 'NonexistentBook'})
        assert len(response.context['books']) == 0

    def test_book_detail_view(self, client, book):
        """Test the book detail view."""
        url = reverse('book_detail', kwargs={'pk': book.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['book'] == book

    def test_book_create_view(self, client, admin_user, category, author):
        """Test the book creation view."""
        client.force_login(admin_user)
        url = reverse('book_create')
        
        # Test GET request
        response = client.get(url)
        assert response.status_code == 200
        
        # Test POST request
        data = {
            'title': 'New Book',
            'isbn': '9780123456789',
            'authors': [author.id],
            'category': category.id,
            'total_copies': 1,
        }
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after success
        assert Book.objects.filter(title='New Book').exists()

    def test_book_update_view(self, client, admin_user, book):
        """Test the book update view."""
        client.force_login(admin_user)
        url = reverse('book_update', kwargs={'pk': book.pk})
        
        # Test GET request
        response = client.get(url)
        assert response.status_code == 200
        
        # Test POST request
        data = {
            'title': 'Updated Title',
            'isbn': book.isbn,
            'authors': [author.id for author in book.authors.all()],
            'category': book.category.id,
            'total_copies': book.total_copies,
        }
        response = client.post(url, data)
        assert response.status_code == 302
        book.refresh_from_db()
        assert book.title == 'Updated Title'

@pytest.mark.django_db
class TestAuthorViews:
    def test_author_list_view(self, client, admin_user, author):
        """Test the author list view."""
        client.force_login(admin_user)
        url = reverse('author_list')
        response = client.get(url)
        assert response.status_code == 200
        assert list(response.context['authors']) == [author]

    def test_author_create_view(self, client, admin_user):
        """Test the author creation view."""
        client.force_login(admin_user)
        url = reverse('author_create')
        
        # Test GET request
        response = client.get(url)
        assert response.status_code == 200
        
        # Test POST request
        data = {
            'first_name': 'Jules',
            'last_name': 'Verne',
            'birth_date': '1828-02-08',
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Author.objects.filter(last_name='Verne').exists()

@pytest.mark.django_db
class TestLoanViews:
    def test_loan_list_view(self, client, admin_user, loan):
        """Test the loan list view."""
        client.force_login(admin_user)
        url = reverse('loan_list')
        response = client.get(url)
        assert response.status_code == 200
        assert list(response.context['loans']) == [loan]

    def test_loan_create_view(self, client, admin_user, book, user):
        """Test the loan creation view."""
        client.force_login(admin_user)
        url = reverse('loan_create')
        
        # Test GET request
        response = client.get(url)
        assert response.status_code == 200
        
        # Test POST request
        return_date = timezone.now() + timedelta(days=14)
        data = {
            'book': book.id,
            'borrower': user.id,
            'return_due_date': return_date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Loan.objects.filter(book=book, borrower=user).exists()

    def test_loan_return_view(self, client, admin_user, loan):
        """Test the loan return view."""
        client.force_login(admin_user)
        url = reverse('loan_return', kwargs={'pk': loan.pk})
        
        # Test GET request
        response = client.get(url)
        assert response.status_code == 200
        
        # Test POST request
        initial_copies = loan.book.available_copies
        response = client.post(url)
        assert response.status_code == 302
        
        # Verify book is returned and available copies increased
        loan.refresh_from_db()
        assert loan.return_date is not None
        assert loan.status == 'C'
        loan.book.refresh_from_db()
        assert loan.book.available_copies == initial_copies + 1

@pytest.mark.django_db
class TestLoginRequired:
    """Test that views require login."""
    
    def test_protected_views(self, client):
        """Test that protected views redirect to login."""
        protected_urls = [
            reverse('book_create'),
            reverse('book_update', kwargs={'pk': 1}),
            reverse('book_delete', kwargs={'pk': 1}),
            reverse('author_list'),
            reverse('author_create'),
            reverse('author_update', kwargs={'pk': 1}),
            reverse('author_delete', kwargs={'pk': 1}),
            reverse('loan_list'),
            reverse('loan_create'),
            reverse('loan_return', kwargs={'pk': 1}),
        ]
        
        for url in protected_urls:
            response = client.get(url)
            assert response.status_code == 302  # Redirect to login
            assert '/login/' in response.url 
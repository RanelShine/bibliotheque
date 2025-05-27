import pytest
from django.utils import timezone
from datetime import timedelta
from catalogue.forms import AuthorForm, BookForm, LoanForm, BookSearchForm

@pytest.mark.django_db
class TestAuthorForm:
    def test_valid_author_form(self):
        """Test that form is valid with correct data."""
        form = AuthorForm({
            'first_name': 'Victor',
            'last_name': 'Hugo',
            'biography': 'French novelist',
            'birth_date': '1802-02-26',
        })
        assert form.is_valid()

    def test_invalid_author_form(self):
        """Test that form is invalid with missing required fields."""
        form = AuthorForm({})
        assert not form.is_valid()
        assert 'first_name' in form.errors
        assert 'last_name' in form.errors

@pytest.mark.django_db
class TestBookForm:
    def test_valid_book_form(self, category, author):
        """Test that form is valid with correct data."""
        form = BookForm({
            'title': 'Les Misérables',
            'isbn': '9781234567890',
            'authors': [author.id],
            'category': category.id,
            'summary': 'A great novel',
            'total_copies': 3,
            'publication_date': '1862-01-01',
        })
        assert form.is_valid()

    def test_invalid_isbn(self, category, author):
        """Test that form is invalid with incorrect ISBN."""
        form = BookForm({
            'title': 'Les Misérables',
            'isbn': '123',  # Invalid ISBN
            'authors': [author.id],
            'category': category.id,
            'total_copies': 3,
        })
        assert not form.is_valid()
        assert 'isbn' in form.errors

    def test_negative_copies(self, category, author):
        """Test that form is invalid with negative copies."""
        form = BookForm({
            'title': 'Les Misérables',
            'isbn': '9781234567890',
            'authors': [author.id],
            'category': category.id,
            'total_copies': -1,
        })
        assert not form.is_valid()

@pytest.mark.django_db
class TestLoanForm:
    def test_valid_loan_form(self, book, user):
        """Test that form is valid with correct data."""
        return_date = timezone.now() + timedelta(days=14)
        form = LoanForm({
            'book': book.id,
            'borrower': user.id,
            'return_due_date': return_date.strftime('%Y-%m-%d %H:%M:%S'),
        })
        assert form.is_valid()

    def test_past_return_date(self, book, user):
        """Test that form is invalid with past return date."""
        past_date = timezone.now() - timedelta(days=1)
        form = LoanForm({
            'book': book.id,
            'borrower': user.id,
            'return_due_date': past_date.strftime('%Y-%m-%d %H:%M:%S'),
        })
        assert not form.is_valid()
        assert 'return_due_date' in form.errors

@pytest.mark.django_db
class TestBookSearchForm:
    def test_empty_search_form(self):
        """Test that empty search form is valid."""
        form = BookSearchForm({})
        assert form.is_valid()

    def test_search_form_with_data(self, category):
        """Test search form with all fields filled."""
        form = BookSearchForm({
            'query': 'Les Misérables',
            'category': category.id,
            'available_only': True,
        })
        assert form.is_valid() 
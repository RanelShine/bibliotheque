import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from catalogue.models import Author, Book, Category, Loan

@pytest.mark.django_db
class TestAuthorModel:
    def test_author_creation(self):
        """Test the creation of an author."""
        author = Author.objects.create(
            first_name="Victor",
            last_name="Hugo",
            birth_date="1802-02-26"
        )
        assert str(author) == "Victor Hugo"
        assert author.first_name == "Victor"
        assert author.last_name == "Hugo"

@pytest.mark.django_db
class TestCategoryModel:
    def test_category_creation(self):
        """Test the creation of a category."""
        category = Category.objects.create(
            name="Roman",
            description="Romans littéraires"
        )
        assert str(category) == "Roman"
        assert category.description == "Romans littéraires"

@pytest.mark.django_db
class TestBookModel:
    @pytest.fixture
    def category(self):
        return Category.objects.create(name="Roman")

    @pytest.fixture
    def author(self):
        return Author.objects.create(first_name="Victor", last_name="Hugo")

    def test_book_creation(self, category, author):
        """Test the creation of a book."""
        book = Book.objects.create(
            title="Les Misérables",
            isbn="9781234567890",
            category=category,
            total_copies=3,
            available_copies=3
        )
        book.authors.add(author)
        
        assert str(book) == "Les Misérables"
        assert book.isbn == "9781234567890"
        assert book.total_copies == 3
        assert book.available_copies == 3
        assert book.is_available == True
        assert list(book.authors.all()) == [author]

@pytest.mark.django_db
class TestLoanModel:
    @pytest.fixture
    def setup_loan(self):
        category = Category.objects.create(name="Roman")
        author = Author.objects.create(first_name="Victor", last_name="Hugo")
        book = Book.objects.create(
            title="Les Misérables",
            isbn="9781234567890",
            category=category
        )
        book.authors.add(author)
        user = User.objects.create_user(username="testuser", password="testpass")
        return book, user

    def test_loan_creation(self, setup_loan):
        """Test the creation and status of a loan."""
        book, user = setup_loan
        loan_date = timezone.now()
        return_due_date = loan_date + timedelta(days=14)
        
        loan = Loan.objects.create(
            book=book,
            borrower=user,
            loan_date=loan_date,
            return_due_date=return_due_date,
            status='B'
        )
        
        assert str(loan) == f"Les Misérables - testuser"
        assert loan.status == 'B'
        assert loan.is_overdue() == False

    def test_loan_overdue(self, setup_loan):
        """Test the overdue status of a loan."""
        book, user = setup_loan
        loan_date = timezone.now() - timedelta(days=15)
        return_due_date = loan_date + timedelta(days=14)
        
        loan = Loan.objects.create(
            book=book,
            borrower=user,
            loan_date=loan_date,
            return_due_date=return_due_date,
            status='B'
        )
        
        assert loan.is_overdue() == True 
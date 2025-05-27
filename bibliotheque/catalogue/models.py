from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """
    Model representing a book category.
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    """
    Model representing a book in the library.
    """
    title = models.CharField(max_length=200)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    authors = models.ManyToManyField(Author, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    summary = models.TextField(blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    publication_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        """Check if the book has any available copies."""
        return self.available_copies > 0

class Loan(models.Model):
    """
    Model representing a book loan.
    """
    LOAN_STATUS = (
        ('B', 'Borrowed'),
        ('R', 'Reserved'),
        ('A', 'Available'),
        ('O', 'Overdue'),
        ('C', 'Completed'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(default=timezone.now)
    return_due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=LOAN_STATUS, default='B')

    class Meta:
        ordering = ['-loan_date']

    def __str__(self):
        return f"{self.book.title} - {self.borrower.username}"

    def is_overdue(self):
        """Check if the loan is overdue."""
        if not self.return_date and timezone.now() > self.return_due_date:
            return True
        return False

from django.contrib import admin
from .models import Book, Author, Category, Loan

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'death_date')
    list_filter = ('birth_date', 'death_date')
    search_fields = ('first_name', 'last_name')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'category', 'total_copies', 'available_copies')
    list_filter = ('category', 'authors')
    search_fields = ('title', 'isbn', 'authors__last_name')
    filter_horizontal = ('authors',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower', 'loan_date', 'return_due_date', 'return_date', 'status')
    list_filter = ('status', 'loan_date', 'return_due_date')
    search_fields = ('book__title', 'borrower__username')
    date_hierarchy = 'loan_date'

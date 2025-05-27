from django import forms
from .models import Book, Author, Category, Loan
from django.utils import timezone
from datetime import timedelta

class AuthorForm(forms.ModelForm):
    """Form for creating and updating authors."""
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'biography', 'birth_date', 'death_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BookForm(forms.ModelForm):
    """Form for creating and updating books."""
    class Meta:
        model = Book
        fields = ['title', 'isbn', 'authors', 'category', 'summary', 
                 'total_copies', 'publication_date']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'authors': forms.SelectMultiple(attrs={'class': 'select2'}),
        }

    def clean_isbn(self):
        """Validate ISBN format."""
        isbn = self.cleaned_data['isbn']
        if not isbn.isdigit() or len(isbn) != 13:
            raise forms.ValidationError("ISBN must be a 13-digit number.")
        return isbn

    def clean(self):
        """Validate that available copies don't exceed total copies."""
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')
        if total_copies is not None and total_copies < 0:
            raise forms.ValidationError("Total copies cannot be negative.")
        return cleaned_data

class LoanForm(forms.ModelForm):
    """Form for creating and managing loans."""
    class Meta:
        model = Loan
        fields = ['book', 'borrower', 'return_due_date']
        widgets = {
            'return_due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available books
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)

    def clean_return_due_date(self):
        """Validate that return date is in the future."""
        return_date = self.cleaned_data['return_due_date']
        if return_date < timezone.now():
            raise forms.ValidationError("Return date must be in the future.")
        return return_date

class BookSearchForm(forms.Form):
    """Form for searching books."""
    query = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by title or author...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    available_only = forms.BooleanField(
        required=False,
        initial=False,
        label='Show only available books'
    ) 
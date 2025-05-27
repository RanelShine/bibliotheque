from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Book, Author, Category, Loan
from .forms import BookForm, AuthorForm, LoanForm, BookSearchForm

def book_list(request):
    """Display list of books with search functionality."""
    form = BookSearchForm(request.GET)
    books = Book.objects.all()

    if form.is_valid():
        if form.cleaned_data['query']:
            query = form.cleaned_data['query']
            books = books.filter(
                Q(title__icontains=query) |
                Q(authors__first_name__icontains=query) |
                Q(authors__last_name__icontains=query)
            ).distinct()
        
        if form.cleaned_data['category']:
            books = books.filter(category=form.cleaned_data['category'])
        
        if form.cleaned_data['available_only']:
            books = books.filter(available_copies__gt=0)

    return render(request, 'catalogue/book_list.html', {
        'books': books,
        'form': form
    })

@login_required
def book_create(request):
    """Create a new book."""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been created.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    
    return render(request, 'catalogue/book_form.html', {
        'form': form,
        'title': 'Add Book'
    })

def book_detail(request, pk):
    """Display book details."""
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'catalogue/book_detail.html', {'book': book})

@login_required
def book_update(request, pk):
    """Update a book."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been updated.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'catalogue/book_form.html', {
        'form': form,
        'title': 'Edit Book'
    })

@login_required
def book_delete(request, pk):
    """Delete a book."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, f'Book "{book.title}" has been deleted.')
        return redirect('book_list')
    return render(request, 'catalogue/book_confirm_delete.html', {'book': book})

@login_required
def loan_create(request):
    """Create a new loan."""
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            book = loan.book
            
            if book.available_copies > 0:
                book.available_copies -= 1
                book.save()
                loan.save()
                messages.success(request, f'Book "{book.title}" has been loaned.')
                return redirect('loan_list')
            else:
                messages.error(request, f'Book "{book.title}" is not available.')
    else:
        form = LoanForm()
    
    return render(request, 'catalogue/loan_form.html', {
        'form': form,
        'title': 'New Loan'
    })

@login_required
def loan_list(request):
    """Display list of loans."""
    loans = Loan.objects.filter(return_date__isnull=True)
    return render(request, 'catalogue/loan_list.html', {'loans': loans})

@login_required
def loan_return(request, pk):
    """Process a book return."""
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        if not loan.return_date:
            loan.return_date = timezone.now()
            loan.status = 'C'
            loan.save()
            
            book = loan.book
            book.available_copies += 1
            book.save()
            
            messages.success(request, f'Book "{book.title}" has been returned.')
        return redirect('loan_list')
    return render(request, 'catalogue/loan_return.html', {'loan': loan})

@login_required
def author_list(request):
    """Display list of authors."""
    authors = Author.objects.all()
    return render(request, 'catalogue/author_list.html', {'authors': authors})

@login_required
def author_create(request):
    """Create a new author."""
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Author "{author}" has been created.')
            return redirect('author_list')
    else:
        form = AuthorForm()
    
    return render(request, 'catalogue/author_form.html', {
        'form': form,
        'title': 'Add Author'
    })

@login_required
def author_update(request, pk):
    """Update an author."""
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Author "{author}" has been updated.')
            return redirect('author_list')
    else:
        form = AuthorForm(instance=author)
    
    return render(request, 'catalogue/author_form.html', {
        'form': form,
        'title': 'Edit Author'
    })

@login_required
def author_delete(request, pk):
    """Delete an author."""
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        author.delete()
        messages.success(request, f'Author "{author}" has been deleted.')
        return redirect('author_list')
    return render(request, 'catalogue/author_confirm_delete.html', {'author': author})

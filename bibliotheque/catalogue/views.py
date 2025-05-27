from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Book, Author, Category, Loan
from .forms import BookForm, AuthorForm, LoanForm, BookSearchForm
from django.contrib.auth.forms import UserCreationForm

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
            messages.success(request, f'Le livre "{book.title}" a été créé avec succès.')
            return redirect('catalogue:book_detail', pk=book.pk)
    else:
        form = BookForm()
    
    return render(request, 'catalogue/book_form.html', {
        'form': form,
        'title': 'Ajouter un livre'
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
            messages.success(request, f'Le livre "{book.title}" a été mis à jour avec succès.')
            return redirect('catalogue:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'catalogue/book_form.html', {
        'form': form,
        'title': 'Modifier le livre'
    })

@login_required
def book_delete(request, pk):
    """Delete a book."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, f'Le livre "{book.title}" a été supprimé avec succès.')
        return redirect('catalogue:book_list')
    return render(request, 'catalogue/book_confirm_delete.html', {'book': book})

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
            messages.success(request, f'L\'auteur "{author}" a été créé avec succès.')
            return redirect('catalogue:author_list')
    else:
        form = AuthorForm()
    
    return render(request, 'catalogue/author_form.html', {
        'form': form,
        'title': 'Ajouter un auteur'
    })

@login_required
def author_update(request, pk):
    """Update an author."""
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'L\'auteur "{author}" a été mis à jour avec succès.')
            return redirect('catalogue:author_list')
    else:
        form = AuthorForm(instance=author)
    
    return render(request, 'catalogue/author_form.html', {
        'form': form,
        'title': 'Modifier l\'auteur'
    })

@login_required
def author_delete(request, pk):
    """Delete an author."""
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        author.delete()
        messages.success(request, f'L\'auteur "{author}" a été supprimé avec succès.')
        return redirect('catalogue:author_list')
    return render(request, 'catalogue/author_confirm_delete.html', {'author': author})

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
                messages.success(request, f'Le livre "{book.title}" a été emprunté avec succès.')
                return redirect('catalogue:loan_list')
            else:
                messages.error(request, f'Le livre "{book.title}" n\'est pas disponible.')
    else:
        form = LoanForm()
    
    return render(request, 'catalogue/loan_form.html', {
        'form': form,
        'title': 'Nouvel emprunt'
    })

@login_required
def loan_list(request):
    """Display list of loans."""
    if request.user.is_staff:
        loans = Loan.objects.all().order_by('-created_at')
    else:
        loans = Loan.objects.filter(borrower=request.user).order_by('-created_at')
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
            
            messages.success(request, f'Le livre "{book.title}" a été retourné avec succès.')
        return redirect('catalogue:loan_list')
    return render(request, 'catalogue/loan_return.html', {'loan': loan})

def register(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form}) 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Book, Loan
from .forms import LoanForm, BookForm

@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'catalogue/book_list.html', {'books': books})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'catalogue/book_detail.html', {'book': book})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, "Le livre a été créé avec succès.")
            return redirect('catalogue:book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'catalogue/book_form.html', {'form': form, 'action': 'Créer'})

@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, "Le livre a été mis à jour avec succès.")
            return redirect('catalogue:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'catalogue/book_form.html', {'form': form, 'action': 'Modifier'})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, "Le livre a été supprimé avec succès.")
        return redirect('catalogue:book_list')
    return render(request, 'catalogue/book_confirm_delete.html', {'book': book})

@login_required
def loan_create(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.borrower = request.user
            loan.save()
            messages.success(request, "Le prêt a été enregistré avec succès.")
            return redirect('catalogue:loan_list')
    else:
        book_id = request.GET.get('book')
        initial = {}
        if book_id:
            book = get_object_or_404(Book, pk=book_id)
            initial['book'] = book
        form = LoanForm(initial=initial)
    return render(request, 'catalogue/loan_form.html', {'form': form})

@login_required
def loan_list(request):
    if request.user.is_staff:
        loans = Loan.objects.all().order_by('-created_at')
    else:
        loans = Loan.objects.filter(borrower=request.user).order_by('-created_at')
    return render(request, 'catalogue/loan_list.html', {'loans': loans})

@login_required
def loan_return(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if request.method == 'POST':
        loan.returned = True
        loan.returned_date = timezone.now()
        loan.save()
        messages.success(request, "Le livre a été retourné avec succès.")
        return redirect('catalogue:loan_list')
    return render(request, 'catalogue/loan_return.html', {'loan': loan}) 
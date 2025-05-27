from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Book, Author, Category, Loan
from .serializers import (
    BookSerializer, AuthorSerializer,
    CategorySerializer, LoanSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Category instances."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Author instances."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name']

class BookViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Book instances."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'isbn', 'authors__last_name']

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """Reserve a book if it's available."""
        book = self.get_object()
        if book.available_copies > 0:
            # Create a loan with 'Reserved' status
            loan = Loan.objects.create(
                book=book,
                borrower=request.user,
                status='R',
                return_due_date=timezone.now() + timezone.timedelta(days=1)
            )
            book.available_copies -= 1
            book.save()
            return Response({
                'status': 'success',
                'message': f'Book "{book.title}" has been reserved.'
            })
        return Response({
            'status': 'error',
            'message': 'Book is not available for reservation.'
        }, status=400)

class LoanViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Loan instances."""
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['book__title', 'borrower__username']

    def get_queryset(self):
        """Filter loans to show only those belonging to the current user unless staff."""
        if self.request.user.is_staff:
            return Loan.objects.all()
        return Loan.objects.filter(borrower=self.request.user)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Return a borrowed book."""
        loan = self.get_object()
        if loan.return_date is None:
            loan.return_date = timezone.now()
            loan.status = 'C'
            loan.save()
            
            book = loan.book
            book.available_copies += 1
            book.save()
            
            return Response({
                'status': 'success',
                'message': f'Book "{book.title}" has been returned.'
            })
        return Response({
            'status': 'error',
            'message': 'This book has already been returned.'
        }, status=400) 
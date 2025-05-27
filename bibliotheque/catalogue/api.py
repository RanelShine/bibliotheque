from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Book, Author, Category, Loan
from .serializers import (
    BookSerializer, AuthorSerializer,
    CategorySerializer, LoanSerializer
)

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to edit.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Category instances."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class AuthorViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Author instances."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name']

class BookViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Book instances."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'isbn', 'authors__last_name']

    def perform_create(self, serializer):
        """Ensure available_copies is set correctly on creation."""
        if 'available_copies' not in serializer.validated_data:
            serializer.validated_data['available_copies'] = serializer.validated_data.get('total_copies', 0)
        serializer.save()

    def perform_update(self, serializer):
        """Ensure available_copies doesn't exceed total_copies on update."""
        instance = self.get_object()
        if 'total_copies' in serializer.validated_data:
            new_total = serializer.validated_data['total_copies']
            if 'available_copies' not in serializer.validated_data:
                # Adjust available copies proportionally
                if instance.total_copies > 0:
                    ratio = instance.available_copies / instance.total_copies
                    serializer.validated_data['available_copies'] = min(
                        int(new_total * ratio),
                        new_total
                    )
                else:
                    serializer.validated_data['available_copies'] = new_total
        serializer.save()

    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """Reserve a book if it's available."""
        book = self.get_object()
        if book.available_copies > 0:
            # Create a loan with 'Reserved' status
            loan = Loan.objects.create(
                book=book,
                borrower=request.user,
                status='B',
                return_due_date=timezone.now() + timezone.timedelta(days=14)
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
        }, status=status.HTTP_400_BAD_REQUEST)

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

    def perform_create(self, serializer):
        """Ensure the book is available and update its available copies."""
        book = serializer.validated_data['book']
        if book.available_copies <= 0:
            raise serializer.ValidationError({
                'book': 'This book is not available for loan.'
            })
        
        # Set the borrower to the current user if not specified
        if 'borrower' not in serializer.validated_data:
            serializer.validated_data['borrower'] = self.request.user

        # Set default status and return_due_date if not specified
        if 'status' not in serializer.validated_data:
            serializer.validated_data['status'] = 'B'
        if 'return_due_date' not in serializer.validated_data:
            serializer.validated_data['return_due_date'] = timezone.now() + timezone.timedelta(days=14)

        # Save the loan and update the book's available copies
        loan = serializer.save()
        book.available_copies -= 1
        book.save()

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Return a borrowed book."""
        loan = self.get_object()
        if loan.status != 'C':  # Not already returned
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
        }, status=status.HTTP_400_BAD_REQUEST) 
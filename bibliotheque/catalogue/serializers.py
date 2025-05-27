from rest_framework import serializers
from .models import Book, Author, Category, Loan

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model."""
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'biography', 'birth_date', 'death_date']

class BookSerializer(serializers.ModelSerializer):
    """Serializer for the Book model."""
    authors = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='authors',
        write_only=True,
        many=True
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'authors', 'author_ids', 'category', 
                 'category_id', 'summary', 'total_copies', 'available_copies',
                 'publication_date', 'created_at', 'updated_at']
        read_only_fields = ['available_copies', 'created_at', 'updated_at']

class LoanSerializer(serializers.ModelSerializer):
    """Serializer for the Loan model."""
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book',
        write_only=True
    )
    borrower_username = serializers.CharField(source='borrower.username', read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'book', 'book_id', 'borrower_username', 'loan_date',
                 'return_due_date', 'return_date', 'status']
        read_only_fields = ['loan_date', 'status'] 
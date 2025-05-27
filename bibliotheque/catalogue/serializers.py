from rest_framework import serializers
from django.utils import timezone
from .models import Book, Author, Category, Loan

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        """Validate that the category name is unique."""
        if Category.objects.filter(name__iexact=value).exists():
            if self.instance and self.instance.name.lower() == value.lower():
                return value
            raise serializers.ValidationError("Une catégorie avec ce nom existe déjà.")
        return value

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model."""
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'biography', 'birth_date', 'death_date']

    def validate(self, data):
        """Validate that death_date is after birth_date if both are provided."""
        birth_date = data.get('birth_date')
        death_date = data.get('death_date')
        if birth_date and death_date and death_date < birth_date:
            raise serializers.ValidationError({
                'death_date': "La date de décès doit être postérieure à la date de naissance."
            })
        return data

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
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'authors', 'author_ids', 'category', 
                 'category_id', 'summary', 'total_copies', 'available_copies',
                 'publication_date', 'created_at', 'updated_at', 'is_available']
        read_only_fields = ['available_copies', 'created_at', 'updated_at']

    def validate_isbn(self, value):
        """Validate ISBN format and uniqueness."""
        # Remove hyphens and spaces
        isbn = ''.join(value.split())
        
        # Check if it's a valid ISBN-13
        if len(isbn) != 13 or not isbn.isdigit():
            raise serializers.ValidationError(
                "L'ISBN doit être au format ISBN-13 (13 chiffres)."
            )

        # Check uniqueness
        if Book.objects.filter(isbn=isbn).exists():
            if self.instance and self.instance.isbn == isbn:
                return value
            raise serializers.ValidationError("Un livre avec cet ISBN existe déjà.")
        
        return value

    def validate_total_copies(self, value):
        """Validate that total_copies is positive."""
        if value < 0:
            raise serializers.ValidationError(
                "Le nombre total d'exemplaires doit être positif."
            )
        return value

    def validate_publication_date(self, value):
        """Validate that publication_date is not in the future."""
        if value and value > timezone.now().date():
            raise serializers.ValidationError(
                "La date de publication ne peut pas être dans le futur."
            )
        return value

class LoanSerializer(serializers.ModelSerializer):
    """Serializer for the Loan model."""
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book',
        write_only=True
    )
    borrower_username = serializers.CharField(source='borrower.username', read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'book', 'book_id', 'borrower_username', 'loan_date',
                 'return_due_date', 'return_date', 'status', 'days_overdue',
                 'is_overdue']
        read_only_fields = ['loan_date', 'status', 'days_overdue', 'is_overdue']

    def validate_return_due_date(self, value):
        """Validate that return_due_date is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "La date de retour prévue doit être dans le futur."
            )
        return value

    def validate(self, data):
        """Validate the entire loan object."""
        if self.instance:
            # Updating existing loan
            if self.instance.status == 'C' and data.get('return_date'):
                raise serializers.ValidationError({
                    'return_date': "Impossible de modifier un prêt déjà retourné."
                })
        else:
            # Creating new loan
            book = data.get('book')
            if book and book.available_copies <= 0:
                raise serializers.ValidationError({
                    'book': "Ce livre n'est pas disponible pour l'emprunt."
                })
        return data 
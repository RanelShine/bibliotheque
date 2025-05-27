from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import api

# Create a router for our API views
router = DefaultRouter()
router.register(r'books', api.BookViewSet)
router.register(r'authors', api.AuthorViewSet)
router.register(r'categories', api.CategoryViewSet)
router.register(r'loans', api.LoanViewSet)

app_name = 'catalogue'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),

    # Book URLs
    path('', views.book_list, name='book_list'),
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Author URLs
    path('authors/', views.author_list, name='author_list'),
    path('author/add/', views.author_create, name='author_create'),
    path('author/<int:pk>/edit/', views.author_update, name='author_update'),
    path('author/<int:pk>/delete/', views.author_delete, name='author_delete'),

    # Loan URLs
    path('loans/', views.loan_list, name='loan_list'),
    path('loan/add/', views.loan_create, name='loan_create'),
    path('loan/<int:pk>/return/', views.loan_return, name='loan_return'),
] 
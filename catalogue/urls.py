from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    # URLs pour les livres
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/create/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    
    # URLs pour les prêts
    path('loan/add/', views.loan_create, name='loan_create'),
    path('loans/', views.loan_list, name='loan_list'),  # URL pour la liste des prêts
    path('loan/<int:loan_id>/return/', views.loan_return, name='loan_return'),  # URL pour le retour de prêt
] 
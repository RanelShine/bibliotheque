# Système de Gestion de Bibliothèque

Une application web Django pour la gestion d'une bibliothèque, permettant aux bibliothécaires de gérer leur catalogue de livres, les auteurs et les emprunts des utilisateurs.

## Fonctionnalités

- Gestion complète des livres (ajout, modification, suppression)
- Gestion des auteurs
- Système d'emprunt et de retour de livres
- Système de réservation
- Recherche de livres par titre, auteur ou catégorie
- API REST complète
- Interface d'administration Django
- Tests unitaires et d'intégration

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- virtualenv (recommandé)

## Installation

1. Cloner le dépôt :
```bash
git clone <url-du-depot>
cd bibliotheque
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix
venv\Scripts\activate     # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Appliquer les migrations :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

## Utilisation

1. Démarrer le serveur de développement :
```bash
python manage.py runserver
```

2. Accéder à l'application :
- Interface web : http://localhost:8000/
- Administration : http://localhost:8000/admin/
- API REST : http://localhost:8000/catalogue/api/

## API REST

L'API REST fournit les endpoints suivants :

- `/catalogue/api/books/` - Gestion des livres
- `/catalogue/api/authors/` - Gestion des auteurs
- `/catalogue/api/categories/` - Gestion des catégories
- `/catalogue/api/loans/` - Gestion des emprunts

Chaque endpoint supporte les opérations CRUD standard (GET, POST, PUT, DELETE).

## Tests

Pour exécuter les tests avec la couverture :

```bash
pytest --cov=catalogue
```

## Structure du Projet

```
bibliotheque/
├── catalogue/              # Application principale
│   ├── models.py          # Modèles de données
│   ├── views.py           # Vues Django
│   ├── api.py             # Vues de l'API REST
│   ├── serializers.py     # Sérialiseurs REST
│   ├── forms.py           # Formulaires
│   ├── urls.py            # Configuration des URLs
│   └── tests/             # Tests
├── bibliotheque/          # Configuration du projet
└── requirements.txt       # Dépendances
```

## Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 
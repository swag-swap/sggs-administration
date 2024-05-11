from django.shortcuts import render, redirect
from .models import Book
from django.contrib.auth.decorators import login_required
from django.db import models
 
@login_required
def home(request): 
    if not request.user.is_librarian == 1:
        return render(request, 'base/404.html')
    recent_arrivals = Book.objects.order_by('-publication_date')[:3]  

    total_books = Book.objects.count()
    total_available_copies = Book.objects.aggregate(total_available=models.Sum('available_copies'))['total_available']
    
    context = {
        'total_books': total_books,
        'total_available_copies': total_available_copies,
        'recent_arrivals': recent_arrivals, 
    }
    return render(request, 'library/home.html', context)


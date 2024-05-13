from django.urls import path, include
from . import views 

urlpatterns = [ 
    path('', views.home, name='library_home'),

    path('book/list/', views.book_list, name='library_book_list'),
    path('book/add/', views.book_add, name='library_book_add'),
    path('book/add/excel/', views.add_books_from_excel, name='library_book_add_excel'),
    path('book/delete/<int:book_id>', views.book_delete, name='library_book_delete'),

    path('book/borrow/list/',views.borrower_list, name='library_book_borrow_list'),
    path('book/borrow/',views.borrow_book, name='library_book_borrow'),
    path('book/return/',views.return_book, name='library_book_return'),


    path('send/email/',views.send_reminder_email, name='library_send_reminder_email'),
]

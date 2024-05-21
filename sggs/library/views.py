from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Borrower
from administration.models import *
from django.contrib.auth.decorators import login_required
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import * 
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from administration.views import parse_excel
 
@login_required
def home(request): 
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')
    recent_arrivals = Book.objects.order_by('-publication_date')[:3]  

    total_books = Book.objects.count()
    total_available_copies = Book.objects.aggregate(total_available=models.Sum('available_copies'))['total_available']
    
    context = {
        'user':request.user,
        'is_librarian': True,
        'total_books': total_books,
        'total_available_copies': total_available_copies,
        'recent_arrivals': recent_arrivals, 
    }
    return render(request, 'library/home.html', context)

def book_list(request):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')
    all_books = Book.objects.all()
 
    title = request.GET.get('title')
    author = request.GET.get('author')
    department = request.GET.get('department')

    if title:
        all_books = all_books.filter(title__icontains=title)
    if author:
        all_books = all_books.filter(author__icontains=author)
    if department:
        all_books = all_books.filter(department__name__icontains=department)
 
    paginator = Paginator(all_books, 10)   
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger: 
        books = paginator.page(1)
    except EmptyPage: 
        books = paginator.page(paginator.num_pages)

    context = {
        'books': books,
        'is_librarian': True,
        'user':request.user,
    }
    return render(request, 'library/book_list.html', context)

def book_add(request):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('library_book_list')   
    else:
        form = BookForm()
    return render(request, 'library/book_add.html', {'user':request.user,'form': form, 'is_librarian': True})

def add_books_from_excel(request):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')  
    
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            excel_data = parse_excel(excel_file)
        except Exception as e: 
            return render(request, 'library/books_add_excel.html', {'user':request.user, 'error': f"Error parsing Excel file: {e}, 'is_librarian': True"})
         
        added_books = []
        updated_books = []
        errors = []
        try:
            for row in excel_data: 
                sr_no = row.get('Sr. No.','')
                title = row.get('Title', '')
                author = row.get('Author', '')
                department_name = str(row.get('Department','')).strip()
                department = None if not department_name else Department.objects.filter(name__iexact=department_name).first() 
                edition = row.get('Edition', '')
                publication_date = row.get('Publication_date','2000-01-01')
                isbn = row.get('ISBN','')
                total_copies = row.get('Total_copies', 0)
                available_copies = row.get('Available_copies',total_copies)
                fine_rate = row.get('Fine_rate',7) 
                

                # a new Book instance with the extracted details
                try:
                    book, created = Book.objects.get_or_create(isbn=isbn,defaults={
                        'title':title,
                        'author':author,
                        'department': department,
                        'edition':edition,
                        'publication_date': publication_date, 
                        'fine_rate':fine_rate, 
                    })
                    if not created:
                        book.title = title
                        book.author = author
                        book.department = department
                        book.edition = edition
                        book.publication_date = publication_date
                        book.available_copies += available_copies
                        book.total_copies += total_copies
                        book.fine_rate = fine_rate
                        book.save()
                        updated_books.append(book) 
                    else:
                        book.available_copies = available_copies
                        book.total_copies = total_copies
                        book.save()                    
                        added_books.append(book)
                except Exception as e: 
                    errors.append(f"Error creating book with sr_no ({sr_no}): {e}")
        except Exception as e:
            errors.append(f"Error creating book with sr_no ({sr_no}): {e}")
        return render(request, 'library/books_add_excel.html', {'user':request.user, 'added_books': added_books, 'updated_books': updated_books, 'errors': errors, 'is_librarian': True})
     
    return render(request, 'library/books_add_excel.html', {'form': BookForm(), 'is_librarian': True})

def book_delete(request, book_id):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')  
    book = get_object_or_404(Book, id=book_id)
    print(book, "HIIII")
    book.delete() 
    return redirect('library_book_list')
 



def borrow_book(request):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')  
    
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        isbn = request.POST.get('isbn').strip()
        if username and isbn:
            user = CustomUser.objects.get(username=username)
            book = Book.objects.get(isbn=isbn) 
            previous_borrow = Borrower.objects.filter(book=book, borrower=user, return_date=None).first()
            if previous_borrow:
                return render(request, 'library/borrow_book.html', {'user': request.user,'book':book, 'message':f"User '{username}' already have the book '{isbn}'", 'is_librarian': True})
            Borrower.objects.create(book=book, borrower=user)
            if book.available_copies<=0:
                return render(request, 'library/borrow_book.html', {'user': request.user,'book':book, 'message':f"No book present of isbn number {isbn}. All books are borrowed", 'is_librarian': True})
            book.available_copies -= 1
            book.save()
            return render(request, 'library/borrow_book.html', {'user': request.user,'book':book, 'message':"Entry done for user: {username} & book: {isbn}...", 'is_librarian': True})
        else:
            return render(request, 'library/borrow_book.html',{'user':request.user, 'message': "Enter correct username or isbn number", 'is_librarian': True})
    else: 
        return render(request, 'library/borrow_book.html', {'user':request.user, 'is_librarian': True})

def return_book(request):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')  
    
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        isbn = request.POST.get('isbn').strip()
        if username and isbn:
            user = CustomUser.objects.get(username=username)
            book = Book.objects.get(isbn=isbn)  
            returner = Borrower.objects.filter(book=book, borrower=user, return_date=None).first()
            print(returner)
            if not returner:
                Borrower.objects.create(book=book, borrower=user, return_date=timezone.now())
            else:
                returner.return_date = timezone.now()
                returner.save()
                book.available_copies += 1
            book.save()
            return render(request, 'library/return_book.html', {'user':request.user,'book':book, 'message':"Entry done for return by user: {username} & book: {isbn}", 'is_librarian': True})
        else:
            return render(request, 'library/return_book.html',{'user':request.user, 'message': "Enter correct username or isbn number", 'is_librarian': True})
    else: 
        return render(request, 'library/return_book.html', {'user':request.user, 'is_librarian': True})

def borrower_list(request):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')  
    
    borrowers = Borrower.objects.all()

    # Filtering
    borrower_name = request.GET.get('borrower_name')
    book_isbn = request.GET.get('book_isbn')
    return_date = request.GET.get('return_date')
    borrow_date = request.GET.get('borrow_date')
    
    if borrower_name:
        borrowers = borrowers.filter(borrower__username__icontains=borrower_name)
    if book_isbn:
        borrowers = borrowers.filter(book__isbn__icontains=book_isbn)
    if return_date:
        borrowers = borrowers.filter(return_date__date=return_date)
    else:
        borrowers = borrowers.filter(return_date__isnull=True)
    if borrow_date:
        borrowers = borrowers.filter(borrowed_date__date=borrow_date) 

    # Pagination
    paginator = Paginator(borrowers, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'library/borrower_list.html', {'user':request.user, 'page_obj': page_obj, 'is_librarian':True})



def send_reminder_email(request):
    if not request.user.is_authenticated or not request.user.is_librarian == 1:
        return render(request, 'base/404.html')   
    if request.method == 'POST':
        overdue_borrowers = Borrower.objects.filter(return_date__isnull=True, borrowed_date__lte=timezone.now() - timedelta(days=7))
        to_email = []
        for borrower in overdue_borrowers: 
            to_email.push(borrower.borrower.email)
        subject = 'Library Book Renewal Reminder'
        message = render_to_string('library/renewal_reminder.html')
        from_email = request.user.email
        send_mail(subject, message, from_email, to_email)

        return render(request, 'library/send_remainder_email.html', {'user':request.user, 'is_librarian': True, 'message': "Remainder sent"})
    
    return render(request, 'library/send_remainder_email.html', {'user':request.user, 'is_librarian': True})
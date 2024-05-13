from django.db import models
from administration.models import *
from django.db.models.signals import pre_delete

class Librarian(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name = 'Librarian')

class Librarian_edited(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name = 'Librarian_edited')

class Book(models.Model): 
    title = models.CharField(max_length=200, default=None, null=True)
    author = models.CharField(max_length=100, default=None, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,default=None, null=True)
    edition = models.CharField(max_length=50, default=None, null=True)
    publication_date = models.DateField(default=None, null=True)
    isbn = models.CharField(max_length=13, unique=True, default=None, null=True)
    available_copies = models.IntegerField(default=1)
    total_copies = models.IntegerField(default = 1)
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    fine_rate = models.IntegerField(default = 1, null=True)

    def __str__(self):
        return self.title
    
@receiver(pre_delete, sender=Book)
def delete_book_cover_image(sender, instance, **kwargs):
    if instance.cover_image:
        if os.path.isfile(instance.cover_image.path):
            os.remove(instance.cover_image.path)

class Borrower(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    borrowed_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f"{self.book.title} - {self.borrower.username}"
    
class ReadingEntry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(default=None, null=True)

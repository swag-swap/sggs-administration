from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Librarian)
admin.site.register(Librarian_edited)
admin.site.register(Book)
admin.site.register(Borrower)
admin.site.register(ReadingEntry)

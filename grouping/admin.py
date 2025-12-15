from django.contrib import admin
from .models import Student, Group

# This tells Django: "Show these tables in the Admin Panel"
admin.site.register(Student)
admin.site.register(Group)
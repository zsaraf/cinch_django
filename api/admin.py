from django.contrib import admin

# Register your models here.
from api.models import User
from api.models import Student
from api.models import Tutor

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Tutor)
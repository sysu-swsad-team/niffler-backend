from django.contrib import admin

# Register your models here.
from .models import Profile,Task,Tag,Participantship

admin.site.register([Profile,Participantship,Task,Tag])
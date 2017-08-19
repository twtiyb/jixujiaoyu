from django.contrib import admin

# Register your models here.
from polls.models import *

admin.site.register(User)
admin.site.register(Invent)
admin.site.register(Pay)
admin.site.register(Account)


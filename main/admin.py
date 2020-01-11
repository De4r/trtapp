from django.contrib import admin
from .models import UploadedFile, ParametersModel
# Register your models here.

admin.site.register(UploadedFile)
admin.site.register(ParametersModel)

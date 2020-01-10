from django import forms

from .models import UploadedFile


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('file_name', 'file_object', 'file_desc', 'file_tag')

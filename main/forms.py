from django import forms

from .models import UploadedFile, ParametersModel


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('file_name', 'file_object', 'file_desc', 'file_tag')


class ParametersModelForm(forms.ModelForm):
    class Meta:
        model = ParametersModel
        fields = ('model_name', 'model_desc', 'chosen_file',
                 'qv', 'q', 'v', 'cp_m', 'ro_m', 'mi_m', 'lam_m',
                 'cp', 'ro', 'alfa', 'T_g', 'H', 'D_b', 'd_out', 'd_inn', 'r_g')

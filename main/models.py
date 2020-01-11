from django.db import models
import datetime

# Create your models here.


class UploadedFile(models.Model):
    file_name = models.CharField(max_length=100)
    file_object = models.FileField(upload_to='files')
    upload_date = models.DateTimeField(auto_now_add=True)
    file_desc = models.TextField(max_length=2000, default='')
    file_tag = models.CharField(max_length=20, default='ZSZI')

    def __str__(self):
        return self.file_name

    def delete(self, *args, **kwargs):
        self.file_object.delete()
        super().delete(*args, **kwargs)


class ParametersModel(models.Model):
    # Standard parameters
    model_name = models.CharField(max_length=250)
    model_desc = models.TextField(max_length=2000, default='')
    chosen_file = models.CharField(max_length=100)
    # Test parameters
    qv = models.FloatField()
    q = models.FloatField()
    v = models.FloatField()
    # Medium properties
    cp_m = models.FloatField()
    ro_m = models.FloatField()
    mi_m = models.FloatField()
    lam_m = models.FloatField()
    # Rock properties
    cp = models.FloatField()
    ro = models.FloatField()
    alfa = models.FloatField()
    # BHE properties
    H = models.FloatField()
    D_b = models.FloatField()
    d_out = models.FloatField()
    d_inn = models.FloatField()
    r_g = models.FloatField()

    created_date = models.DateTimeField(
        auto_now_add=True)

    def __str__(self):
        return self.model_name

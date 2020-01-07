from django.db import models

# Create your models here.


class UploadedFile(models.Model):
    file_name = models.CharField(max_length=100)
    file_object = models.FileField(upload_to='files')
    upload_date = models.DateTimeField(auto_now_add=True)
    file_desc = models.TextField(max_length=2000, default='')
    

    def __str__(self):
        return self.file_name

    def delete(self, *args, **kwargs):
        self.file_object.delete()
        super().delete(*args, **kwargs)

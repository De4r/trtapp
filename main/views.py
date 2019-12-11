from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from .models import UploadedFile
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import FileSystemStorage
from .forms import UploadedFileForm

# Create your views here.

def homepage(request):
    return render(request, 'main/home.html')

def trt(request):
    return render(request, 'main/trt.html')

def files_list_view(request):
    uploaded_files = UploadedFile.objects.all().order_by('-upload_date')
    return render(request, 'main/files_list.html', {
        'files': uploaded_files,
    })

def solver_view(request):
    return render(request, 'main/solver.html')

def parameters_view(request):
    return render(request, 'main/parameters.html')

def upload_file(request):
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('main:files_list')
    else:
        form = UploadedFileForm()
    return render(request, 'main/upload_file.html', {
        'form': form,
    })

def delete_file(request, pk):
    if request.method == 'POST':
        file_to_delete = UploadedFile.objects.get(pk=pk)
        file_to_delete.delete()
    return redirect('main:files_list')

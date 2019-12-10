from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
# from .models import Post, UploadedFile
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
# from .forms import UploadedFileForm

# Create your views here.

def homepage(request):
    return render(request, 'main/home.html')

def trt(request):
    return render(request, 'main/trt.html')

def files_view(request):
    return render(request, 'main/files.html')

def solver_view(request):
    return render(request, 'main/solver.html')

def parameters_view(request):
    return render(request, 'main/parameters.html')
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from .models import UploadedFile
from .forms import UploadedFileForm
from plotly.offline import plot
# from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd
import os
from django.conf import settings
from .mFuncs import plotIsp
# Create your views here.


def homepage(request):

    return render(request, 'main/home.html')


def isp_view(request):
    uploaded_files = UploadedFile.objects.filter(
        file_tag='ISP').order_by('-upload_date')
    if request.method == 'POST':
        chosen_file = request.POST.get('chosen_file')
        f = UploadedFile.objects.get(file_name=chosen_file)
        plot_div = plotIsp(f)
        
    else:
        f = uploaded_files[0]
        plot_div = plotIsp(f)
    
    return render(request, 'main/isp.html',
                      context={'files': uploaded_files,
                               'plot_div': plot_div,
                               'file': f})


def trt(request):
    return render(request, 'main/trt.html')


def files_list_view(request):
    uploaded_files = UploadedFile.objects.all().order_by('-upload_date')
    return render(request, 'main/files_list.html', {
        'files': uploaded_files,
    })


def solver_view(request):
    x_data = [0, 1, 2, 3]
    y_data = [x**2 for x in x_data]

    plot_div = plot([go.Scatter(x=x_data, y=y_data,
                                mode='lines', name='test',
                                opacity=0.8, marker_color='green')],
                    output_type='div', include_plotlyjs=False)

    return render(request, 'main/solver.html',
                  context={'plot_div': plot_div})


def parameters_view(request):
    if request.method == 'POST':
        chosen_file = request.POST.get('chosen_file')
        f = UploadedFile.objects.get(file_name=chosen_file)
        file_path = os.path.join(
            settings.BASE_DIR, f.file_object.url[1:]).replace('\\', '/')
        print(file_path)

    uploaded_files = UploadedFile.objects.all().order_by('-upload_date')

    return render(request, 'main/parameters.html',
                  context={'files': uploaded_files, })


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

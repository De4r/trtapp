from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse
from .models import UploadedFile, ParametersModel
from .forms import UploadedFileForm, ParametersModelForm
from plotly.offline import plot
# from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd
import os
from django.conf import settings
from .ispFuncs import plotIsp
from .trtFuncs import Trt
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
                           'file': f,
                           'plot_shown': True,})


def trt(request):
    return render(request, 'main/trt.html')


def files_list_view(request):
    uploaded_files = UploadedFile.objects.all().order_by('-upload_date')
    return render(request, 'main/files_list.html', {
        'files': uploaded_files,
    })


def solver_view(request):
    parameters_models = ParametersModel.objects.all().order_by('-created_date')
    if request.method == 'POST':
        chosen_model = request.POST.get('chosen_model')
        opts = request.POST.dict()
        p_model = ParametersModel.objects.get(model_name=chosen_model)
        print(p_model, opts)
        trt = Trt(p_model, opts)
        plot_div = trt.handle_all()
        params = None
        if 'fit_lin' in opts:
            if opts['fit_lin'] == '1':
                params = trt.yield_params()
        
        return render(request, 'main/solver.html',
                  context={'plot_div': plot_div,
                  'models': parameters_models,
                  'opts': opts,
                  'plot_shown': True,
                  'params': params,
                  })
    else:
        plot_div = None
    return render(request, 'main/solver.html',
                  context={'plot_div': plot_div,
                  'models': parameters_models})


def parameters_list_view(request):
    parameters_models = ParametersModel.objects.all().order_by('-created_date')
    return render(request, 'main/parameters_list.html', {
        'models': parameters_models, })


def parameters_show_view(request, pk=1):
    parameter_model = ParametersModel.objects.get(pk=pk)

    return render(request, 'main/parameters_show.html', {
        'model': parameter_model,
    })


def parameters_view(request):
    if request.method == 'POST':
        form = ParametersModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main:parameters_list')
        else:
            print(form.errors)

    else:
        form = ParametersModelForm()
    uploaded_files = UploadedFile.objects.all().order_by('-upload_date')

    return render(request, 'main/parameters.html',
                  context={'files': uploaded_files,
                           'form': form, })


def parameters_edit_view(request, pk_param=None):
    # contet_instance = RequestConext(request)

    if request.method == 'POST':
        instance = None
        try:
            pk_param = request.POST['pk_param']
            instance = ParametersModel.objects.get(pk=pk_param)
        except:
            pass

        if instance is None:
            return redirect('main:parameters')
        else:
            form = ParametersModelForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('main:parameters_list')
            else:
                print(form.errors)
    else:
        try:
            instance = ParametersModel.objects.get(pk=pk_param)
            print(instance)
        except:
            pass
        form = ParametersModelForm(instance=instance)

    uploaded_files = UploadedFile.objects.all().order_by('-upload_date')

    return render(request, 'main/parameters_edit.html',
                  context={'files': uploaded_files,
                           'form': form,
                           'pk_param': pk_param, })


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


def delete_file(request, pk_file):
    if request.method == 'POST':
        file_to_delete = UploadedFile.objects.get(pk=pk_file)
        file_to_delete.delete()
    return redirect('main:files_list')


def delete_parameters_model(request, pk_param):
    if request.method == 'POST':
        model_to_delete = ParametersModel.objects.get(pk=pk_param)
        model_to_delete.delete()
    return redirect('main:parameters_list')

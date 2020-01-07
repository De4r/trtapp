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
# Create your views here.


def homepage(request):

    return render(request, 'main/home.html')


def isp_view(request):
    # ylabel = ['Temp. *C', 'Cisn. hPa', 'Poz. nasw. lx.']
    f = UploadedFile.objects.get(file_name='ISP')
    filename = f.file_object.url[1:]
    filename = os.path.join(settings.BASE_DIR, filename).replace('\\', '/')

    df = pd.read_csv(filename)
    df['Time'] = pd.to_datetime(df['Time'], unit='s')
    df['Time'] = df['Time'].dt.tz_localize(
        "GMT").dt.tz_convert('Europe/Warsaw')
    plot_div = []

    for i, temp in zip(range(3), ('T_', 'P_', 'L_')):
        fig = go.Figure()
        for j in range(3):
            col = temp+str(j)
            fig.add_trace(go.Scatter(
                x=df['Time'], y=df[col], mode="lines", name=col))

        plot_div.append(plot(fig,
                             output_type='div', include_plotlyjs=False))

    return render(request, 'main/isp.html',
                  context={'plot_div': plot_div,
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

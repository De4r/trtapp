"""trtapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('trt/', views.trt, name='trt'),
    path('trt/files_list', views.files_list_view, name='files_list'),
    path('trt/upload_file', views.upload_file, name='upload_file'),
    path('trt/delete_file<int:pk_file>', views.delete_file, name='delete_file'),
    path('trt/solver', views.solver_view, name='solver'),
    path('trt/parameters', views.parameters_view, name='parameters'),
    path('trt/parameters_edit<int:pk_param>',
         views.parameters_edit_view, name='parameters_edit'),
    path('trt/parameters_list', views.parameters_list_view, name='parameters_list'),
    path('trt/parameters_show<int:pk>',
         views.parameters_show_view, name='parameters_show'),
    path('trt/delete_parameters_model<int:pk_param>',
         views.delete_parameters_model, name='delete_parameters_model'),
    path('isp/', views.isp_view, name='isp'),
]

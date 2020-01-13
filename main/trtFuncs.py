import numpy as np
import pandas as pd
import plotly.offline as plt
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from .models import UploadedFile, ParametersModel
from .trtlib.trt_func import *
import os
from django.conf import settings

temp_cols = ['t','T_in', 'T_out', 'T_surr']
other_cols = ['t', 'Q_v', 'v', 'Q']


class Trt():
    def __init__(self, p_model):
        self.model = p_model
        f = UploadedFile.objects.get(file_name=p_model.chosen_file)
        filename = f.file_object.url[1:]
        self.filename = os.path.join(
            settings.BASE_DIR, filename).replace('\\', '/')
        self.df = pd.read_csv(filename)
        self.df = checkTemperatureScale(self.df)

    def plot_raw_data(self):
        try:
            plot_div = []
            if 'T_surr' in self.df.columns.values:
                fig = createPlot(self.df[temp_cols])
            else:
                fig = createPlot(self.df[temp_cols[:-1]])
            plot_div.append(
                plt.plot(fig, output_type='div', include_plotlyjs=False))

            if other_cols[1] in self.df.columns.values:
                fig = createPlot(self.df[other_cols[:2]], ylabel=1, title=-2)
                plot_div.append(
                    plt.plot(fig, output_type='div', include_plotlyjs=False))
            
            return plot_div
        except Exception as e:
            return e

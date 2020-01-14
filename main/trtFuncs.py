import numpy as np
import pandas as pd
import plotly.offline as plt
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from .models import UploadedFile, ParametersModel
from .trtlib.trt_func import *
import os
from django.conf import settings

temp_cols = ['t', 'T_in', 'T_out', 'T_surr']
other_cols = ['t', 'Q_v', 'v', 'Q']


class Trt():
    def __init__(self, p_model, opts):
        self.model = p_model
        f = UploadedFile.objects.get(file_name=p_model.chosen_file)
        filename = f.file_object.url[1:]
        self.filename = os.path.join(
            settings.BASE_DIR, filename).replace('\\', '/')
        self.df = pd.read_csv(filename)
        self.df = checkTemperatureScale(self.df)
        self.options = opts
        self.xlabel = 0

    def handle_plot(self):
        self.handle_time()
        self.handle_time_window()
        self.handle_ma()

        return self.plot_data()

    def handle_time_window(self):
        if 't_1' in self.options:
            if self.options['t_1'] != '':
                t_1 = float(self.options['t_1'])
            else:
                t_1 = 0

            if 't_2' in self.options:
                if self.options['t_2'] != '':
                    t_2 = float(self.options['t_2'])
                else:
                    t_2 = 0

            if t_1 != 0 and t_2 != 0:
                self.df = trimData(self.df, 't', t_1, t_2)
            elif t_1 != 0:
                self.df = trimData(self.df, 't', t_1)
            else:
                pass

    def handle_time(self):
        if 'log_scale' in self.options and int(self.options['log_scale']) == True:
            self.df['t'] = timeToLogScale(self.df['t'])
            self.xlabel = 1

    def handle_ma(self):
        if self.check_bool('mean_mode'):
            # check for position and win_len
            if self.check_number('win_len'):
                window_len = int(self.options['win_len'])
            else:
                window_len = 5
            if self.check_bool('win_pos'):
                center = True
            else:
                center = False
            cols = self.df.columns[1:]
            print(cols)
            self.df[cols] = calcMovingAverage(
                self.df[cols], window_len=window_len, center=center)


    def plot_data(self, xlabel=0):
        try:
            plot_div = []
            if 'T_surr' in self.df.columns.values:
                fig = createPlot(self.df[temp_cols], xlabel=xlabel)
            else:
                fig = createPlot(self.df[temp_cols[:-1]], xlabel=xlabel)
            plot_div.append(
                plt.plot(fig, output_type='div', include_plotlyjs=False))

            if other_cols[1] in self.df.columns.values:
                fig = createPlot(self.df[other_cols[:2]],
                                 ylabel=1, title=-2, xlabel=xlabel)
                plot_div.append(
                    plt.plot(fig, output_type='div', include_plotlyjs=False))

            return plot_div
        except Exception as e:
            return e

    def check_bool(self, arg):
        if arg in self.options and int(self.options[arg]) == True:
            return True
        else:
            return False

    def check_number(self, arg):
        if arg in self.options and self.options[arg] != '':
            return True
        else:
            return False

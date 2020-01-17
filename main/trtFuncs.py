import numpy as np
import pandas as pd
import plotly.offline as plt
import plotly.graph_objects as go
# from sklearn.linear_model import LinearRegression # no space on free hostings
from .models import UploadedFile, ParametersModel
from .trtlib.trt_func import *
import os
from django.conf import settings

temp_cols = ['t', 'T_in', 'T_out', 'T_surr', 'T_f']
o_cols = ['t', 'Q_v', 'v', 'Q']


class Trt():
    def __init__(self, p_model, opts):
        self.model = p_model
        f = UploadedFile.objects.get(file_name=p_model.chosen_file)
        filename = f.file_object.url[1:]
        self.filename = os.path.join(
            settings.BASE_DIR, filename).replace('\\', '/')
        print(self.filename)
        self.df = pd.read_csv(filename)
        self.df = checkTemperatureScale(self.df)
        self.T_g2 = self.df[temp_cols[1:3]].iloc[0].mean()
        print(self.T_g2)
        self.options = opts
        self.xlabel = 0

    def yield_params(self):
        params = {'Q_mean': self.Q_mean, 'lambda': self.lam, 'rb': self.rb}
        if self.v_mean:
            params['v_mean'] = self.v_mean
        if self.Qv_mean:
            params['Qv_mean'] = self.Qv_mean

        return params

    def handle_all(self):
        self.handle_time()
        self.handle_time_window()
        # we analize in Window now
        self.handle_velocity()
        self.handle_flow()
        self.handle_heat()
        # calc average here
        self.handle_ma()
        # others below are based on smoothed data
        self.handle_tf()
        self.handle_fit_model()

        self.calc_params()

        return self.plot_data()

    def calc_params(self):
        if self.check_bool('fit_lin'):
            if self.model.H is not None:
                self.lam = calculateLambda(
                    Q=self.Q_mean, H=self.model.H, k=self.modelParams[0])
                if self.model.T_g is not None:
                    self.rb = calcRb(H=self.model.H, Q=self.Q_mean,
                                     m=self.modelParams[1], Tg=self.model.T_g, 
                                     lam=self.lam, ro=self.model.ro, cp=self.model.cp, 
                                     r0=self.model.D_b/2)
                else:
                    self.rb = calcRb(H=self.model.H, Q=self.Q_mean,
                                     m=self.modelParams[1], Tg=self.T_g2, 
                                     lam=self.lam, ro=self.model.ro, cp=self.model.cp, 
                                     r0=self.model.D_b/2)
            print(self.lam, self.rb)


    def handle_heat(self):
        # check if Q column was provided
        if o_cols[3] in self.df.columns.values:
            self.Q_mean = self.df[o_cols[3]].mean()
        # if not check if Q_v was calculated
        elif o_cols[1] in self.df.columns.values:
            # if so check other variables
            if self.model.cp_m is not None and self.model.ro_m is not None:
                # then calculate new column
                cols = temp_cols[1:3]
                cols.append(o_cols[1])
                self.df[o_cols[3]] = calculateHeatPower(
                    self.df[cols], ro=self.model.ro_m, cp=self.model.cp_m)
                self.Q_mean = self.df[o_cols[3]].mean()
            else:
                raise ValueError("Something went wrong in Q_v*ro*cp")
        else:
            if self.Qv_mean:
                # there is a Q_v field so will calc by T diff
                if self.model.cp_m is not None and self.model.ro_m is not None:
                    self.df[o_cols[3]] = calculateHeatPower(
                        self.df[temp_cols[1:3]], ro=self.model.ro_m, 
                        cp=self.model.cp_m, Qv=self.Qv_mean)
                    self.Q_mean = self.df[o_cols[3]].mean()
                else:
                    raise ValueError("Something went wrong in Qv_mean*ro*cp")
            elif self.model.q is not None:
                self.Q_mean = self.model.q
            else:
                raise ValueError("Any Q cant be calculated")
        print(self.Q_mean)

    def handle_flow(self):
        # check if a Q_v column was provided
        if o_cols[1] in self.df.columns.values:
            self.Qv_mean = self.df[o_cols[1]].mean()
        # check if colum v was provided
        elif o_cols[2] in self.df.columns.values:
            if self.model.d_inn is not None:  # check d_inn * v
                self.df[o_cols[1]] = calculateFlow(
                    self.df[o_cols[2]].values, d_inn=self.model.d_inn)
            elif self.model.d_out is not None and self.model.r_g is not None:  # check d_out-2r_g * v
                self.df[o_cols[1]] = calculateFlow(
                    self.df[o_cols[2]].values, d_out=self.model.d_out, r_g=self.model.r_g)
            else:
                raise ValueError("No pipe dimension provided")
        else:
            if self.v_mean:
                if self.model.d_inn is not None:  # check d_inn * v
                    self.Qv_mean = calculateFlow(
                        self.v_mean, d_inn=self.model.d_inn)
                elif self.model.d_out is not None and self.model.r_g is not None:  # check d_out-2r_g * v
                    self.Qv_mean = calculateFlow(
                        self.v_mean, d_out=self.model.d_out, r_g=self.model.r_g)
                else:
                    raise ValueError("No pipe dimension provided")
            elif self.model.qv is not None:
                self.Qv_mean = self.model.qv
            else:
                raise ValueError("No flow field provided. Checked 'Q_v', 'v'.")
        print(self.Qv_mean)

    def handle_velocity(self):
        if o_cols[2] in self.df.columns.values:
            self.v_mean = df[o_cols[2]].mean()
            print(self.v_mean)
        else:
            if self.model.v is not None:
                self.v_mean = self.model.v
                print(self.v_mean)
            else:
                print("No velocity provided")

    def handle_fit_model(self):
        if self.check_bool('fit_lin') and self.check_bool('show_tf'):
            self.modelParams = fitModelSciPy(
                self.df[[temp_cols[0], temp_cols[-1]]])

    def handle_tf(self):
        if self.check_bool('show_tf'):
            self.df[temp_cols[-1]] = calculateTf(self.df[temp_cols[1:3]])

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
                self.df = trimData(self.df, temp_cols[0], t_1=t_1, t_2=t_2)
            elif t_1 != 0:
                self.df = trimData(self.df, temp_cols[0], t_1=t_1)
            elif t_2 != 0:
                self.df = trimData(self.df, temp_cols[0], t_2=t_2)
            else:
                pass

    def handle_time(self):
        if self.check_bool('log_scale'):
            self.df[temp_cols[0]] = timeToLogScale(self.df[temp_cols[0]])
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
            # if T_f plot, then 1st
            if 'T_f' in self.df.columns.values:
                if self.check_bool('fit_lin'):
                    fig = plotModels(
                        self.df[['t', 'T_f']], self.modelParams, 0, style=0)
                else:
                    fig = createPlot(
                        self.df[['t', 'T_f']], xlabel=xlabel, title=-1)
                plot_div.append(
                    plt.plot(fig, output_type='div', include_plotlyjs=False))
            # temperature plots
            if 'T_surr' in self.df.columns.values:
                fig = createPlot(self.df[temp_cols[:4]], xlabel=xlabel)
            else:
                fig = createPlot(self.df[temp_cols[:3]], xlabel=xlabel)
            plot_div.append(
                plt.plot(fig, output_type='div', include_plotlyjs=False))

            if o_cols[3] in self.df.columns.values:
                fig = createPlot(self.df[[o_cols[0], o_cols[3]]],
                                 ylabel=2, title=2, xlabel=xlabel)
                plot_div.append(
                    plt.plot(fig, output_type='div', include_plotlyjs=False))

            if o_cols[1] in self.df.columns.values:
                fig = createPlot(self.df[o_cols[:2]],
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

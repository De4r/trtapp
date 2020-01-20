from plotly.offline import plot
# from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd
import os
from django.conf import settings
# Create your views here.


class IspFile():
    def __init__(self, fileObj):
        filename = fileObj.file_object.url[1:]
        self.filename = os.path.join(settings.BASE_DIR, filename).replace('\\', '/')
        print(self.filename)

        self.df = pd.read_csv(self.filename)
        self.df['Time'] = pd.to_datetime(self.df['Time'], unit='s')
        self.df['Time'] = self.df['Time'].dt.tz_localize(
            "GMT").dt.tz_convert('Europe/Warsaw')

    def get_all_stats(self):
        t_stats = self.get_stats('T_')
        p_stats = self.get_stats('P_')
        l_stats = self.get_stats('L_')
        return [t_stats, p_stats, l_stats]

    def get_stats(self, col):
        stats = []
        for j in range(3):
            col_name = col + str(j)
            mean = self.df[col_name].mean()
            max_ = self.df[col_name].max()
            min_ = self.df[col_name].min()
            std = self.df[col_name].std()
            var = self.df[col_name].var()
            temp_dict = {'name': col_name, 'mean': mean, 'max': max_, 'min': min_, 'std': std, 'var': var}
            stats.append(temp_dict)
        return stats

    def plotIsp(self):
        ylabel = ['Temperatura [°C]', 'Ciśnienie [hPa]',
                  'Nateżenie <br> naświetlenia [lx.]']
        xlabel = 'Czas'
        plot_div = []

        for i, temp in zip(range(3), ('T_', 'P_', 'L_')):
            fig = go.Figure()
            for j in range(3):
                col = temp+str(j)
                fig.add_trace(go.Scatter(
                    x=self.df['Time'], y=self.df[col], mode="lines", name=col))
            fig.update_layout(yaxis_title_text=ylabel[i])
            plot_div.append(plot(fig,
                                 output_type='div', include_plotlyjs=False))

        return plot_div

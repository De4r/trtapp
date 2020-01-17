from plotly.offline import plot
# from plotly.subplots import make_subplots
import plotly.graph_objs as go
import pandas as pd
import os
from django.conf import settings
# Create your views here.


def plotIsp(fileObj):
    ylabel = ['Temperatura [°C]', 'Ciśnienie [hPa]', 'Nateżenie <br> naświetlenia [lx.]']
    xlabel = 'Czas'
    
    filename = fileObj.file_object.url[1:]
    filename = os.path.join(settings.BASE_DIR, filename).replace('\\', '/')
    print(filename)

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
        fig.update_layout(yaxis_title_text=ylabel[i])
        plot_div.append(plot(fig,
                             output_type='div', include_plotlyjs=False))
    
    return plot_div
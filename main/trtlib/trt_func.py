import numpy as np
import pandas as pd
import plotly.offline as plt
import plotly.graph_objects as go
# from sklearn.linear_model import LinearRegression, Ridge, Lasso # no space on free hosting
import scipy as sp
from scipy.stats import linregress
from scipy.signal import savgol_filter


""" Assummtions:
df - DataFrame with 1st column as x axis!
All temperatures in C scale, maybe will be conversion
Labels:
t - time colum - seconds
T_in - temperature at inlet
T_out - temperature at outlet
T_surr - temperature of surroundings
T_dif - difference of T_in - T_out
T_f - temperature function for TRT
Qv - volume flow m^3/s
Q - heat power W

Rest of parameters to pass:
Ro - density kg/m^3
Cp -
H - depth of borehole m
R - radius of bore holer m
d_inn - inner diameter of pipe m
d_out - outer diameter of pipe m
r_g - thickness of pipe m
T_g - ground non disturbed temperature
      passed or taken as first temp
alfa - thermal diffusivity of ground [m^2/s]
title - title of figure form globTitles
xlabel, ylabel - title of axis

Parameters:
gamma - euler constant
globTitles, globyAxis, globxAxis, globLineStyles
 """


globTitles = ['Wykres temperatur z TRT',
              'Moc cieplna', 'Przepływ',
              'Funkcja temperatury', 'Prędkość przepływu']
globyLables = ['Temperatura [°C]', 'Przeplyw [m<sup>3</sup>/s]', 'Moc [W]', 'Predkość [m/s]']
globxLabels = ['Czas [s]', 'Czas ln(t) [s]']
globLineStyles = ['lines', 'markers', 'lines+markers']
gamma = 0.5772


def createPlot(df, title=0, ylabel=0, xlabel=0, *args, **kwargs):
    if 'fig' in kwargs:
        add_traces = True
        fig = kwargs.get('fig')
    else:
        add_traces = False
        fig = go.Figure()
    # assuming that df is passed to plot, where 1st colum is x Axis,
    # rest will be plotted with legend as col name !
    if 'style' in kwargs:
        style = kwargs.get('style')
    else:
        style = -1
    
    for col in df.columns[1:]:
        if add_traces:
            fig.add_trace(go.Scatter(
            x=df[df.columns[0]], y=df[col], mode=globLineStyles[style], name=col))
        else:
            fig.add_trace(go.Scatter(
            x=df[df.columns[0]], y=df[col], mode=globLineStyles[style], name=col))

    # titleText = globTitles[title]
    plotTitle = dict(text=globTitles[title], xanchor='center', yanchor='top',
                     font=dict(family='Arial', size=28), x=0.5)

    # ylabelText = globyLables[ylabel]
    yAxisDesc = dict(title=globyLables[ylabel], title_font=dict(
        family='Arial', size=24))

    # xlabelText = globxLabels[xlabel]
    xAxisDesc = dict(title=globxLabels[xlabel], title_font=dict(
        family='Arial', size=24))

    legendDesc = dict(font=dict(family='Arial', size=20))

    fig.update_layout(title=plotTitle, yaxis=yAxisDesc,
                      xaxis=xAxisDesc, legend=legendDesc)
    return fig


def plotMovingAverage(df, window_len=15, min_periods=1, center=False, title=1, ylabel=0, xlabel=0, *args, **kwargs):
    df[df.columns[1:]] = calcMovingAverage(
        df[df.columns[1:]], window_len, min_periods, center)

    fig = createPlot(df, title=title, ylabel=ylabel,
                     xlabel=xlabel, *args, **kwargs)
    titleText = globTitles[title]
    plotTitle = dict(text=f'{titleText}{window_len}', xanchor='center', yanchor='top',
                     font=dict(family='Arial', size=28), x=0.5)
    fig.update_layout(title=plotTitle)
    return fig


# we pass just our t, T_f and models+lambdas data!
def plotModels(df, modelParams, lambdas, title=3, ylabel=0, xlabel=1, *args, **kwargs):
    fig = createPlot(df, title=title, ylabel=ylabel, xlabel=xlabel)
    if 'style' in kwargs:
        style = kwargs.get('style')
    else:
        style = -1
    t = df[df.columns[0]].values
    minx = min(t)
    # maxx = max(t)
    maxy = max(df[df.columns[1]].values)

    model_values = calculateModel(df, modelParams)

    fig.add_trace(go.Scatter(x=t, y=model_values,
                             mode=globLineStyles[style], name=modelParams[3]))
    fig.add_annotation(build_annotation(modelParams, xpos=minx, ypos=maxy))
    return fig


def build_annotation(modelParams, xpos, ypos):
    text = f"Model: {modelParams[3]} <br> k: {round(modelParams[0], 4)} <br> m: {round(modelParams[1], 4)} <br> R ^ 2: {round(modelParams[2], 4)} <br> std_err: {round(modelParams[4], 4)}"
    return go.layout.Annotation(
        x=xpos,
        y=ypos,
        xref="x",
        yref="y",
        text=text,
        showarrow=False,
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#ffffff"
        ),
        align="center",
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#636363",
        ax=-150,
        ay=-50,
        bordercolor="#c7c7c7",
        borderwidth=2,
        borderpad=4,
        bgcolor="#ff7f0e",
        opacity=0.8
    )


def calcMovingAverage(df, window_len=15, min_periods=1, center=False):
    df = df.rolling(window=window_len, min_periods=min_periods,
                    center=center).mean()
    return df


def apply_salv_filter(df, window_len=7, order=3, method='nearest', **kwargs):
    for col in df.columns:
        df[col] = savgol_filter(
            df[col], window_length=window_len, polyorder=order, **kwargs)
    return df


def timeToLogScale(df):
    return np.log(df)


def trimData(df, col, t_1=0, t_2=-1, df_raw=None):
    try:
        id_x = []
        id_x.append(df.loc[df[col] >= t_1].index.values.astype(int)[0])
        if t_2 != -1:
            id_x.append(df.loc[df[col] >= t_2].index.values.astype(int)[0])
        # not working, type error not subscriptable

        print("Trimming to band: ")
        if len(id_x) > 1:
            df = df[id_x[0]:id_x[1]]
            if df_raw is not None:
                df_raw = df_raw[id_x[0]:id_x[1]]
            print(round(df[col].iat[0], 2), round(df[col].iat[-1], 2))
        else:
            df = df[id_x[0]:]
            if df_raw is not None:
                df_raw = df_raw[id_x[0]:]
            print(round(df[col].iat[0], 2), " : end")
        return df, df_raw
    except Exception as e:
        print(e)
        return df, df_raw


# assuming of getting df['T_in', 'T_out', 'Qv'], ro and cp
def calculateHeatPower(df, ro, cp, Qv=None):
    if Qv is None:
        return ro * cp * abs(df[df.columns[-1]] *
                             (df[df.columns[1]] - df[df.columns[0]]))
    else:
        return ro * cp * abs(Qv *
                             (df[df.columns[1]] - df[df.columns[0]]))


# simply pass 2 columns of temperature, return 1 colum with t_f
def calculateTf(df, method='average'):
    if method == 'average':
        # df['T_f'] = (df[df.columns[0]] + df[df.columns[1]])/2
        return (df[df.columns[0]] + df[df.columns[1]])/2
    return df[df.columns[-1]]


# assume to pass df with 2 columns: t, T_F as 0 and 1 colum, turned off for this time
# def fitModel(df, model='linear'):
#     t = df[df.columns[0]].values.reshape(-1, 1)
#     t_f = df[df.columns[1]].values
#     if model == 'linear':
#         model = LinearRegression().fit(t, t_f)
#         modelType = 'linear'
#     elif model == 'ridge':
#         model = Ridge().fit(t, t_f)
#         modelType = 'ridge'
#     elif model == 'lasso':
#         model = Lasso().fit(t, t_f)
#         modelType = 'lasso'
#     else:
#         models = ['linear', 'ridge', 'lasso']
#         modelsParams = []
#         for model in models:
#             modelsParams.append(fitModel(df, model=model))
#         return modelsParams

#     rq = model.score(t, t_f)
#     k = model.coef_[0]
#     m = model.intercept_
#     modelParams = (k, m, rq, modelType)
#     return modelParams


def fitModelSciPy(df):
    t = df[df.columns[0]].values  # .reshape(-1, 1)
    t_f = df[df.columns[1]].values
    modelType = 'linear'
    k, m, rq, p_val, std_err = linregress(x=t, y=t_f)
    modelParams = (k, m, rq**2, modelType, std_err, p_val)
    print(modelParams)
    return modelParams


# assume to pass time and params
def calculateModel(df, modelParams):
    t = df[df.columns[0]].values  # .reshape(-1, 1)
    return np.array(modelParams[0] * t + modelParams[1])


def calculateLambda(Q, H, k):
    return Q / (4 * np.pi * H * k)


def calcualteMinTime(alfa, radius):
    return (5*radius**2)/alfa


# pass df with temp colums
def checkTemperatureScale(df):
    for col in df.columns:
        if min(df[col]) - 273 > 0:
            df[col] = df[col]-273.15
    return df


def calculateFlow(v, d_out=0, d_inn=0, r_g=0):
    if d_inn != 0:
        return np.pi * d_inn**2 * v / 4
    else:
        return (d_out-2*r_g)**2 * np.pi * v / 4


def getLambdas(modelsParams, Q_mean, H):
    lambdas = []
    for i in range(len(modelsParams)):
        lambdas.append(calculateLambda(Q_mean, H, modelsParams[i][0]))
    return lambdas


def calcRb(H, Q, m, Tg, lam, ro, cp, r0):
    temp = H/Q*(m - Tg) - (1/(4*np.pi*lam) *
                           (np.log(4*lam/(ro*cp)/r0**2) - gamma))
    return temp


# old things

# we pass just our t, T_f and models+lambdas data!
# def plotModels(df, modelsParams, lambdas, title=-1, ylabel=0, xlabel=1, *args, **kwargs):
#     fig = createPlot(df, title=title, ylabel=ylabel, xlabel=xlabel)
#     if 'style' in kwargs:
#         style = kwargs.get('style')
#     else:
#         style = -1
#     t = df[df.columns[0]].values
#     minx = min(t)
#     maxx = max(t)
#     maxy = max(df[df.columns[1]].values)
#     if isinstance(modelsParams, list):
#         for i in range(len(modelsParams)):
#             mp = modelsParams[i]
#             xpos = minx + i*(maxx-minx)/5
#             model_values = calculateModel(df, mp)

#             fig.add_trace(go.Scatter(x=t, y=model_values,
#                                      mode=globLineStyles[style], name=mp[-1]))
#             fig.add_annotation(
#                 go.layout.Annotation(
#                     x=xpos,
#                     y=maxy,
#                     xref="x",
#                     yref="y",
#                     text=f"Model: {mp[-1]} <br> k: {round(mp[0], 4)} <br> m: {round(mp[1], 4)} <br> R ^ 2: {round(mp[2], 4)} <br> Lambda: {round(lambdas[i], 4)}",
#                     showarrow=False,
#                     font=dict(
#                         family="Courier New, monospace",
#                         size=18,
#                         color="#ffffff"
#                     ),
#                     align="center",
#                     arrowhead=2,
#                     arrowsize=1,
#                     arrowwidth=2,
#                     arrowcolor="#636363",
#                     ax=-150,
#                     ay=-50,
#                     bordercolor="#c7c7c7",
#                     borderwidth=2,
#                     borderpad=4,
#                     bgcolor="#ff7f0e",
#                     opacity=0.8
#                 ))
#     return fig

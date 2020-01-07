import numpy as np
import pandas as pd
import plotly.offline as plt
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression, Ridge, Lasso


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


globTitles = ['Wykres temperatur z testu reakcji termicznej',
              'Wykres temperature z TRT <br> po usrednieniu oknem: ',
              'Przebieg mocy cieplnej', 'Przebieg przepłwu',
              'Modele regresji liniowej']
globyLables = ['Temperatura [°C]', 'Przeplyw [m^3/s]', 'Moc [W]']
globxLabels = ['Czas [s]', 'Czas ln(t) [s]']
globLineStyles = ['lines', 'markers', 'lines+markers']
gamma = 0.5772


def createPlot(df, title=0, ylabel=0, xlabel=0, *args, **kwargs):
    fig = go.Figure()
    # assuming that df is passed to plot, where 1st colum is x Axis,
    # rest will be plotted with legend as col name !
    if 'style' in kwargs:
        style = kwargs.get('style')
    else:
        style = -1

    for col in df.columns[1:]:
        fig.add_trace(go.Scatter(
            x=df[df.columns[0]], y=df[col], mode=globLineStyles[style], name=col))

    titleText = globTitles[title]
    plotTitle = dict(text=titleText, xanchor='center', yanchor='top',
                     font=dict(family='Arial', size=28), x=0.5)

    ylabelText = globyLables[ylabel]
    yAxisDesc = dict(title=ylabelText, title_font=dict(
        family='Arial', size=24))

    xlabelText = globxLabels[xlabel]
    xAxisDesc = dict(title=xlabelText, title_font=dict(
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
def plotModels(df, modelsParams, lambdas, title=-1, ylabel=0, xlabel=1, *args, **kwargs):
    fig = createPlot(df, title=title, ylabel=ylabel, xlabel=xlabel)
    if 'style' in kwargs:
        style = kwargs.get('style')
    else:
        style = -1
    t = df[df.columns[0]].values
    minx = min(t)
    maxx = max(t)
    maxy = max(df[df.columns[1]].values)
    if isinstance(modelsParams, list):
        for i in range(len(modelsParams)):
            mp = modelsParams[i]
            xpos = minx + i*(maxx-minx)/5
            model_values = calculateModel(df, mp)

            fig.add_trace(go.Scatter(x=t, y=model_values,
                                     mode=globLineStyles[style], name=mp[-1]))
            fig.add_annotation(
                go.layout.Annotation(
                    x=xpos,
                    y=maxy,
                    xref="x",
                    yref="y",
                    text=f"Model: {mp[-1]} <br> k: {round(mp[0], 4)} <br> m: {round(mp[1], 4)} <br> R ^ 2: {round(mp[2], 4)} <br> Lambda: {round(lambdas[i], 4)}",
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
                ))
    return fig


def calcMovingAverage(df, window_len=15, min_periods=1, center=False):
    df = df.rolling(window=window_len, min_periods=min_periods,
                    center=center).mean()
    return df


def timeToLogScale(df):
    return np.log(df)


def trimData(df, col, *args):
    try:
        id_x = []
        if isinstance(col, str):
            for i in range(len(args)):
                id_x.append(df.loc[df[col] >= args[i]].index.values.astype(int)[0])
# not working, type error not subscriptable
        elif isinstance(col, int):
            for i in range(len(args)):
                id_x.append(df.loc[df.columns[col] >= args[i]
                               ].index.values.astype(int)[0])
        print("Trimming to band: ")
        if len(args) > 1:
            df = df[id_x[0]:id_x[1]]
            print(round(df[col].iat[0], 2), round(df[col].iat[-1], 2))
        else:
            df = df[id_x[0]:]
            print(round(df[col].iat[0], 2), " : end")
        return df
    except Exception as e:
        print(e)
        return df


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


# assume to pass df with 2 columns: t, T_F as 0 and 1 colum
def fitModel(df, model='linear'):
    t = df[df.columns[0]].values.reshape(-1, 1)
    t_f = df[df.columns[1]].values
    if model == 'linear':
        model = LinearRegression().fit(t, t_f)
        modelType = 'linear'
    elif model == 'ridge':
        model = Ridge().fit(t, t_f)
        modelType = 'ridge'
    elif model == 'lasso':
        model = Lasso().fit(t, t_f)
        modelType = 'lasso'
    else:
        models = ['linear', 'ridge', 'lasso']
        modelsParams = []
        for model in models:
            modelsParams.append(fitModel(df, model=model))
        return modelsParams

    rq = model.score(t, t_f)
    k = model.coef_[0]
    m = model.intercept_
    modelParams = (k, m, rq, modelType)
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
    temp = H/Q*(m - Tg) - (1/(4*np.pi*lam) * (np.log(4*lam/(ro*cp)/r0**2) - gamma))
    return temp


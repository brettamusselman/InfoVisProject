#Program: dashAttempt.ipynb
#Purpose: Attempt at Dash
#Author: Brett Musselman
#Date Started: 7 August 2023

#import libraries
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

#Import and read from csv cleaned Philadelphia Weather data from OpenWeather API
df = pd.read_csv('PhiladelphiaWeatherForInfoVis.csv')
df['date'] = pd.to_datetime(df['date'])

lineChart = px.line(
        df, x="date", y="temp", color="description", labels={'date': 'Date', 'temp': 'Temperature (F)',
                                                             'description': 'Description'},
                                                     title="Temperature for Each Weather Condition"
    )

boxPlot = px.box(df, y='temp', labels={'temp':'Temperature (F)'})


#Setup layout
app.layout = html.Div(children=[
    html.H1(children='Info Vis Dashboard'),
    html.Div([
            html.Div([
                html.H1(children='Dot Plot'),
                html.Div(children='''
                    First Viz!
                '''),

                dcc.Graph(id='graph-with-slider'),
               
                dcc.RangeSlider(
                    df['clouds'].min(),
                    df['clouds'].max(),
                    step=10,
                    value=[df['clouds'].min(), df['clouds'].max()],
                    marks={str(clouds): str(clouds) for clouds in range(0,101, 10)},
                    id='clouds-slider',
                    updatemode='drag'
                                ),
                
                html.H6(children='Drag Slider to Filter Based On Clouds (%)'),
                
            ], className='eight columns'),
            html.Div([
                html.H1(children='Box Plot'),
                html.Div(children='''
                    Second Viz!
                '''),
            
                dcc.Graph(
                    id='box-plot',
                    figure=boxPlot
                    ),
            ], className='four columns'),
        ], className='row'),
    html.Div([
        html.H1(children='Line Chart'),
        html.Div(children='''
            Third Viz!
        '''),

        dcc.Graph(
            id='line-graph',
            figure=lineChart
            ),
        ], className='row'),
])

#Callbacks
@callback(
    Output('graph-with-slider', 'figure'),
    Input('clouds-slider', 'value'))
def updated_dot_plot(selected_clouds):
    filtered_df = df[df.clouds >= selected_clouds[0]]
    filtered_df = filtered_df[df.clouds <= selected_clouds[1]]

    dotPlot = px.scatter(filtered_df, x='temp', y=filtered_df['date'].dt.month, labels={'temp': 'Temperature (F)',
                                                                                        'y': 'Month (#)',
                                                                                        'humidity': 'Humidity'},
                                                                                        color='humidity')

    dotPlot.update_layout(transition_duration=500)

    return dotPlot


#Run app
if __name__ == '__main__':
    app.run_server(debug=False)

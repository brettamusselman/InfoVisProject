#Program: dashAttempt.ipynb
#Purpose: Attempt at Dash
#Author: Brett Musselman
#Date Started: 7 August 2023

#import libraries
import pandas as pd
import numpy as np
import datetime
import os
import sys
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, callback
from flask import Flask

server = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

#Import and read from csv cleaned Philadelphia Weather data from OpenWeather API
df = pd.read_csv(f'dashAppV1/PhiladelphiaWeatherForInfoVis.csv')
df['date'] = pd.to_datetime(df['date'])

lineChart = px.line(
        df, x="date", y="temp", color="description", labels={'date': 'Date', 'temp': 'Temperature (F)',
                                                             'description': 'Description'},
                                                     title="Temperature for Each Weather Condition"
    )

polarChart = px.scatter_polar(df, r='speed', theta='deg', color='pressure', labels={'speed': 'Wind Speed (meter/sec)',
                                                                                    'deg': 'Wind Direction (degrees)',
                                                                                    'pressure': 'Pressure (hPa)'}, color_continuous_scale='blues')

scatterPlot = px.scatter(df, x='temp', y='feels_like', color='humidity', labels={'temp': ' Actual Temperature (F)',
                                                                                 'feels_like': 'Feels Like Temperature (F)',
                                                                                 'humidity': 'Humidity (%)'}, color_continuous_scale='rdpu')

def generate_table(dataframe, max_rows=6):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

#Setup layout
app.layout = html.Div(children=[
    html.H1(children='Information Visualization Dashboard: Philadelphia Weather'),
    html.H2(children='By: Brett Musselman'),
    html.H6(children='''
                        This dashboard utilizes PANDAS and Plotly to create a Dash app based in Flask.
                        I sourced this data from OpenWeather Historical API and created a CSV from it.
                    '''),
    html.Div([html.A("Link to Tableau",
           href='https://public.tableau.com/views/InformationVisualizationBrettMusselmanPhiladelphiaWeather/Dashboard1?:language=en-US&publish=yes&:display_count=n&:origin=viz_share_link',
           target="_blank")
        ]),
    html.Div([
            html.Div([
                html.H1(children='Dot Plot'),
                html.Div(children='Dot Plot of Temperature and Humidity by Month with Cloudiness Filter'),

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
                html.Div([
                html.H6(children='Drag Slider to Filter Dot Plot Based on Clouds (%)'),
                ], style={'textAlign': 'center'})
                
            ], className='eight columns'),
            html.Div([
                html.H1(children='Box Plot'),
                html.Div(children='''
                    Box Plot of Temperature by Date Range
                '''),
            
                dcc.Graph(
                    id='boxplot-for-date-range',
                    ),
                
                html.Div([
                dcc.DatePickerRange(
                    start_date_placeholder_text="Start Period",
                    end_date_placeholder_text="End Period",
                    calendar_orientation='vertical',
                    start_date=df['date'].min(),
                    end_date=df['date'].max(),
                    id='date-range'
                    ),
                ], style={'textAlign': 'center'}),
                
                html.Div([
                html.H6(children='Adjust Dates to Filter Boxplot'),
                ], style={'textAlign': 'center'})
                
            ], className='four columns'),
        ], className='row'),
    html.Div([
        html.Div([
            html.H1(children='Polar Chart'),
                html.Div(children='''
                    Polar Chart of Wind Speed by Direction with Pressure
                '''),
            
            dcc.Graph(id='polar-chart',
                      figure=polarChart)
            ], className='five columns'),
        html.Div([
            html.H1(children='Scatter Plot'),
                html.Div(children='''
                    Scatter Plot of Feels Like Temperature vs Actual Temperature with Humidity
                '''),
            
            dcc.Graph(id='scatter-plot',
                figure=scatterPlot)
            ], className='seven columns'),
        ], className='row'),
    html.Div([
        html.H1(children='Line Chart'),
        html.Div(children='Line Chart of Temperature Trends over Time by Description'),
        
        html.Div(children='Click Description Legend to Filter Chart', style={'textAlign':'right'}),

        dcc.Graph(
            id='line-graph',
            figure=lineChart
            ),
        ], className='row'),
    html.Div([
        html.H1(children='Head of Table for Dataset'),
        html.H6(children='Data from OpenWeather API from August 7, 2022 to July 30, 2023 for Philadelphia'),
        generate_table(df)
        ], className='row'),
    html.Div([
        html.H1(children='Statistical Description of Columns'),
        html.Div([
            html.H3(children='Select Feature to Change Statistical Description'),
            dcc.Dropdown(options=[{'label': 'Date', 'value': 'date'},
                                  {'label': 'Temperature (F)', 'value': 'temp'},
                                  {'label': 'Feels Like Temperature (F)', 'value': 'feels_like'},
                                  {'label': 'Pressure (hPa)', 'value': 'pressure'},
                                  {'label': 'Humidity (%)', 'value': 'humidity'},
                                  {'label': 'Minimum Temperature (F)', 'value': 'temp_min'},
                                  {'label': 'Maximum Temperature (F)', 'value': 'temp_max'},
                                  {'label': 'Wind Speed (meter/sec)', 'value': 'speed'},
                                  {'label': 'Wind Direction (deg)', 'value': 'deg'},
                                  {'label': 'Gust', 'value': 'gust'},
                                  {'label': 'Clouds (%)', 'value': 'clouds'},
                                  {'label': 'Weather ID', 'value': 'id'},
                                  {'label': 'Main Description', 'value': 'main'},
                                  {'label': 'Weather Description (more in-depth)', 'value': 'description'},
                                  {'label': 'Icon', 'value': 'icon'},],value='date',id='feature-dropdown'),
            html.Div(id='statistical-descriptions',),
            ])
        ], className ='row'),
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
                                                                                        'humidity': 'Humidity (%)'},
                                                                                        color='humidity')

    dotPlot.update_layout(transition_duration=500)

    return dotPlot

@callback(
    Output('boxplot-for-date-range', 'figure'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'))
def updated_box_plot(start_date, end_date):
    filtered_df = df[df.date >= start_date]
    filtered_df = filtered_df[df.date <= end_date]
    
    boxPlot = px.box(filtered_df, y='temp', labels={'temp':'Temperature (F)'})
    
    boxPlot.update_layout(transition_duration=500)

    return boxPlot

@callback(
    Output('statistical-descriptions', 'children'),
    Input('feature-dropdown', 'value')
    )
def updated_stat_description(value):
    described = df[value].describe()
    
    return f'Statistical Description of {value}: {described}'

server = app.server

#Run app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port='8050')
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
df = df.drop('gust', axis=1)
df['date'] = pd.to_datetime(df['date'])
df['temp'] = df['temp'].round()
df['feels_like'] = df['feels_like'].round()
df['temp_max'] = df['temp_max'].round()
df['temp_min'] = df['temp_min'].round()

#df for line chart with only 5 most common conditions
dfl = df.loc[df["description"].isin(["overcast clouds", "scattered clouds", "broken clouds", "few clouds", "clear sky"])]

lineChart = px.line(dfl , x="date", y="temp", facet_col=dfl["description"].map(str.title),
                    labels={'date': 'Date', 'temp': 'Temperature (F)',},
                    title="Temperature for 5 Most Common Weather Conditions", hover_data={'temp': ':.0f'}
    )

lineChart.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

polarChart = px.scatter_polar(df, r='speed', theta='deg', color='pressure', labels={'speed': 'Wind Speed (meter/sec)',
                                                                                    'deg': 'Wind Direction (degrees)',
                                                                                    'pressure': 'Pressure (hPa)'}, color_continuous_scale='blues')

scatterPlot = px.scatter(df, x='temp', y='feels_like', color='humidity', labels={'temp': ' Actual Temperature (F)',
                                                                                 'feels_like': 'Feels Like Temperature (F)',
                                                                                 'humidity': 'Humidity (%)'}, color_continuous_scale='rdpu',
                         hover_data={'temp': ':.0f', 'feels_like': ':.0f'})

def generate_numerical(df):
    df_number = df.select_dtypes(include='number')
    temp_record = {'Variable': [], 'Count': [], 'Mean': [], 'Std': [], 'Min': [], '25%': [], '50%': [], '75%': [], 'Max': []}
    for column in df_number:
        description = str(df_number[column].describe())
        description = description.split()
        temp_record['Variable'].append(column)
        temp_record['Count'].append(round(float(description[1])))
        temp_record['Mean'].append(round(float(description[3]),2))
        temp_record['Std'].append(round(float(description[5]),2))
        temp_record['Min'].append(round(float(description[7])))
        temp_record['25%'].append(round(float(description[9])))
        temp_record['50%'].append(round(float(description[11])))
        temp_record['75%'].append(round(float(description[13])))
        temp_record['Max'].append(round(float(description[15])))
    
    temp_df = pd.DataFrame.from_dict(temp_record)
    return dash_table.DataTable(temp_df.to_dict('records'), [{'name': i, 'id': i} for i in temp_df.columns])

def generate_categorical(df):
    start = True
    df_category = df.select_dtypes(exclude='number')
    temp_record = {'Variable': [], 'Count': [], 'Unique': [], 'Top': [], 'Frequency': []}
    for column in df_category:
        if start == True:
            start = False
            pass
        else:
            description = str(df_category[column].describe())
            description = description.split()
            temp_record['Variable'].append(column)
            temp_record['Count'].append(description[1])
            temp_record['Unique'].append(description[3])
            temp_record['Top'].append(description[5])
            temp_record['Frequency'].append(description[7])
    
    temp_df = pd.DataFrame.from_dict(temp_record)
    return dash_table.DataTable(temp_df.to_dict('records'), [{'name': i, 'id': i} for i in temp_df.columns])

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
        
        html.Div(children='Use Zoom Feature to Explore Differences in Trends', style={'textAlign':'right'}),

        dcc.Graph(
            id='line-graph',
            figure=lineChart
            ),
        ], className='row'),
    html.Center(
        html.Div([
            html.H1(children='Head of Table for Dataset'),
            html.H6(children='Data from OpenWeather API from August 7, 2022 to July 30, 2023 for Philadelphia'),
            generate_table(df)
            ], className='row'),),
    html.Div([
        html.Center(html.H1(children='Statistical Description of Columns')),
        html.Div([
            html.Div([html.H3(children='Description of Numerical Columns'), generate_numerical(df)], className='six columns'),
            html.Div([html.H3(children='Description of Categorical Columns'), generate_categorical(df)], className='six columns'),
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
                                                                                        color='humidity',
                         hover_data={'temp': ':.0f'})

    dotPlot.update_layout(transition_duration=500)

    return dotPlot

@callback(
    Output('boxplot-for-date-range', 'figure'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'))
def updated_box_plot(start_date, end_date):
    filtered_df = df[df.date >= start_date]
    filtered_df = filtered_df[df.date <= end_date]
    
    boxPlot = px.box(filtered_df, y='temp', labels={'temp':'Temperature (F)'}, hover_data={'temp': ':.0f'})
    
    boxPlot.update_layout(transition_duration=500)

    return boxPlot

server = app.server

#Run app
if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port='8050')

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dask.dataframe as dd
import dask.bag as db
from dfFilter import dfFilter
from createFig import *
from retrieveData import retrieveData
from datetime import date, datetime, timedelta
import configparser
import numpy as np


#initialise tokens and master data
dataMaster = retrieveData({"mapbox":"secret_token"})
token = dataMaster.get_all_token()

#master DFs
masterDF =  dataMaster.get_all_covid_csv()

#create dash object
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY], meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1'}])
server = app.server

#define layout------------------------------------------------------------------------------------------------------------------------------------------------------------
#default style
CONTENT_STYLE = {
    "margin-left": "1rem",
    "margin-right": "1rem"
}

TITLE_COLOR = {
    "color":"#0FBC8C"
}
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
#content and their items
myNavBar = html.Div([
    dbc.Navbar([
        
        
        dbc.Nav([
            html.Div([
                dbc.Col(dbc.NavItem(dbc.NavbarBrand(html.Small("COVID-19 Project"),href="#"))),
            ]),
            html.A([
                dbc.DropdownMenu(
                    [dbc.DropdownMenuItem(html.A("LinkedIn"), href = "https://www.linkedin.com/in/pwunlee/"), dbc.DropdownMenuItem(html.A("GitHub"),  href = "https://github.com/PoeWunLee")],
                label="About Me",
                nav=True)
            ],style={"margin-left":"67rem"}),

            html.A([
                dbc.DropdownMenu(
                    [dbc.DropdownMenuItem(html.A("JHU CSSE"), href = "https://github.com/CSSEGISandData/COVID-19"), dbc.DropdownMenuItem(html.A("OWID"),  href = "https://ourworldindata.org/coronavirus")],
                label="Data Source",
                nav=True)
            ],style={"margin-left":"1rem"})
            
            #dbc.NavItem(dbc.NavLink(html.H4("Data Source"), href="https://github.com/CSSEGISandData/COVID-19")),
            
        ], navbar=True)
    ],dark=True, color="primary")
        
], style={"margin-left": "0.25rem","margin-right": "0.25rem", "height":"5"})
#,brand="COVID-19 Dashboard Project",color="primary",dark=True,fluid=True)


myDatePick = dcc.DatePickerSingle(
    id="calendar-pick",
    min_date_allowed = date(2020,1,22),
    max_date_allowed = date(dataMaster.lastUpdate.year,dataMaster.lastUpdate.month, dataMaster.lastUpdate.day),
    initial_visible_month= str(date.today().month),
    date=date(dataMaster.lastUpdate.year,dataMaster.lastUpdate.month, dataMaster.lastUpdate.day),
    style={"width":"100%"}
)

myCards =html.Div([
    dbc.Card([html.P(),html.H5("Confirmed", style={"color":"#66ccff", "text-align":"center"}),dbc.Spinner(dbc.CardBody(id="card-1"))]),
    html.A(),
    dbc.Card([html.P(),html.H5("Deaths", style={"color":"red", "text-align":"center"}), dbc.Spinner(dbc.CardBody(id="card-2"))]),
    html.A(),
    dbc.Card([html.P(),html.H5("Recovered", style={"color":"cyan", "text-align":"center"}),  dbc.Spinner(dbc.CardBody(id="card-3"))]),
    html.A(),
    dbc.Card([html.P(),html.H5("Active", style={"color":"orange", "text-align":"center"}), dbc.Spinner(dbc.CardBody(id="card-4"))])
    
])

myMap = html.Div([
    html.H5("World COVID-19 Map", style=TITLE_COLOR),
    html.Br(),
    dbc.Row(dcc.Loading(id="world-card",type="default", style={"backgroundColor": "transparent"}), justify="center"),
    html.Hr(),
    dbc.Tabs([

        dbc.Tab(tab_id="confirmed",label="Confirmed"),
        dbc.Tab(tab_id="deaths",label="Deaths"),
        dbc.Tab(tab_id="recovered",label="Recovered"),
        dbc.Tab(tab_id="active",label="Active"),
        #dbc.Tab(tab_id="new_cases",label="Infection Incidence Risk"),
        #dbc.Tab(tab_id="new_deaths",label="Death Incidence Risk")
                        
    ],
                            
        id="tabs",
        active_tab="confirmed",
        style={"color":"dark", "width":"10"}
    )
])

myTimeSeries =  html.Div([

    html.H5("Time Series", style=TITLE_COLOR),             
    dbc.Row(dcc.Loading(id="daily-card",type="default",style={"backgroundColor":"transparent"}), justify="center"),
    html.P(),
    dbc.RadioItems(
        id="var-select",
        options = [
                {"label":"Confirmed", "value":"confirmed-option"},
                {"label":"Deaths", "value":"deaths-option"},
                {"label":"Recovered", "value":"recovered-option"},
                {"label":"Active", "value":"active-option"}
            ],
        value = "confirmed-option",
        inline=True
    )
])

myTop5 = html.Div([
    html.H5("Daily Top 5 by Continent", style=TITLE_COLOR),             
    dbc.Row(dcc.Loading(id="watch-mojo",type="default",style={"backgroundColor":"transparent"}), justify="center"),
    html.P(),
    dbc.RadioItems(
        id="var-select-2",
        options = [
                {"label":"Confirmed", "value":"confirmed-option"},
                {"label":"Deaths", "value":"deaths-option"},
                {"label":"Recovered", "value":"recovered-option"}
            ],
        value = "confirmed-option",
        inline=True
    )
])

content = html.Div([
    html.P(),
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([html.Div([html.H5("Display Date", style=TITLE_COLOR), html.P(), myDatePick], style={"text-align":"center"})])),
            #html.H4("Status", style={"color":TITLE_COLOR["color"],"text-align":"center" }),
            html.Br(),
            myCards,
        ],width="30", align="start"),
        dbc.Col(dbc.Jumbotron(dbc.Container([myMap],fluid=True,style={"padding":0})), width="auto",align="start"),
        dbc.Col([
            dbc.Jumbotron(dbc.Container(myTimeSeries,fluid=True ,style={"padding":0})),
            dbc.Jumbotron(dbc.Container(myTop5,fluid=True ,style={"padding":0}))
        ], width="515",align="start")
        
    ], align="start")
        
], style=CONTENT_STYLE)

app.layout = dbc.Container([myNavBar,content],
    fluid=True,
    style={"padding":10}     
)


#callback function: calls the function right below everytime input field is changed--------------------------------------------------------------------------------------
#@ declaration is equivalent to app.callback(thisFunc(input))

@app.callback(
    [Output(component_id="card-1",component_property="children"),
    Output(component_id="card-2",component_property="children"),
    Output(component_id="card-3",component_property="children"),
    Output(component_id="card-4",component_property="children")],

    [Input(component_id="calendar-pick",component_property="date")]
)
def getDateData(selected_date):

    total_list, new_list = dfFilter(masterDF,selected_date).filter_total()
    
    res = [
        [
            html.H5(total_list[i], style={"text-align":"center"}), 
            html.P("{}".format(new_list[i]),style={"text-align":"center"}) 
        ]
    for i in range(4)]
    
    return res[0], res[1], res[2], res[3]


@app.callback(
    Output(component_id="world-card",component_property="children"),
    [Input(component_id="calendar-pick",component_property="date"),
    Input(component_id="tabs",component_property="active_tab")]
)
def generateGraphFromDate(selected_date,tabs):

    
    worldDF = dfFilter(masterDF,selected_date).filter_world()
    fig = dcc.Graph(figure=createChloroplethFig(worldDF,token["mapbox"]).chloropleth_fig(tabs))
    
    return fig

@app.callback(
    Output(component_id="daily-card",component_property="children"),
    [Input(component_id="var-select",component_property="value")]
)
def generateBarGraph(selected_status):

    dailyDF= dfFilter(masterDF,dataMaster.lastUpdate).filter_daily(selected_status)
    fig = dcc.Graph(figure=createDailyBar(dailyDF).daily_bar_fig())

    return fig

@app.callback(
    Output(component_id="watch-mojo",component_property="children"),
    [Input(component_id="calendar-pick",component_property="date"),
    Input(component_id="var-select-2",component_property="value")]
)
def createWatchMojo(thisDate,thisSelect):

    mojoDF = dfFilter(masterDF,thisDate).filter_top_five(thisSelect)
    fig = dcc.Graph(figure=createTop5Fig(mojoDF).top5_fig(thisDate))
    
    return fig

#run if not imported as module
if __name__ == '__main__':
    app.run_server(debug=False)


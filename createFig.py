import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

class createChloroplethFig:

    def __init__(self,df,mapbox_token):
        self.df = df.copy()
        self.fig = None
        self.token = mapbox_token
        self.colorName = None
        self.sizeName = None

    def _get_color_size(self,metric):
        
        #normalised name
        self.sizeName = "{}_size".format(metric)

        #take the metric in question
        self.df = self.df.loc[self.df["status"]==metric]

        thisMax, thisMin = self.df["data"].max(), self.df["data"].min()

        #size
        maxSize = 100
        scale_factor = maxSize/(thisMax - thisMin)
        self.df[self.sizeName] = (self.df["data"]*scale_factor)**(1/2)

        ##color
        colorMetric = metric
        self.colorName = "{}/p.d.".format(colorMetric)

        self.df[self.colorName] = self.df[self.sizeName]/(self.df["population_density"])

        self.df.fillna(value=0,inplace=True)

        #rename data with the metric for display
        self.df.rename(columns={"data":metric},inplace=True)


    
    def chloropleth_fig(self,metric):
        
        #get size and color
        self._get_color_size(metric)

        px.set_mapbox_access_token(self.token)

        #create figure
        self.fig = px.scatter_mapbox(

            self.df,
            lat = "Lat",
            lon = "Long",
            hover_name = "Name",
            hover_data = [metric,self.colorName,"population"],
            color = self.colorName,
            size = self.sizeName,
            color_continuous_scale=px.colors.sequential.Redor,
            size_max = 50,
            zoom = 0.7,
            center = {
                "lat": 35,
                "lon": 12
            }
        )
        
        #update layout figure
        self.fig.update_layout(
            template = "plotly_dark",
            mapbox_style = "dark",
            margin={"r":0,"t":0,"l":0,"b":0},
            height = 700,
            width = 980,
            paper_bgcolor = "#303030"
        )

        
        return self.fig
    
class createDailyBar:

    def __init__(self,df):
        self.df = df
        self.fig = None
    
    def daily_bar_fig(self):
        self.fig = px.bar(self.df,x="date",y=self.df.columns[1])

        self.fig.add_scatter(x=self.df["date"],y=self.df["7 day average"],name="7 days average")

        self.fig.update_layout(
            template="plotly_dark",
            width = 888,
            height = 250,
            margin={"r":0, "t":0, "l":0, "b":0},
            showlegend= False,
            paper_bgcolor = "#303030",
            plot_bgcolor = "#303030"   
        )

        return self.fig


class createTop5Fig:

    def __init__(self,df):
        self.df = df
        self.fig = None
    
    def top5_fig(self,myDate):
        countryLabel = self.df["Name"].to_numpy().reshape(6,5).T

        self.fig = go.Figure(data=[
            go.Bar(
                name="{}".format(i), 
                y=self.df.loc[self.df["colorLabel"]==i-1]["continent"], 
                x=self.df.loc[self.df["colorLabel"]==i-1][myDate],
                width=0.3,
                orientation="h",
                text=countryLabel[i-1],
                customdata = self.df.loc[self.df["colorLabel"]==i-1]["percent_continent"],
                hovertemplate= "<b>%{text}</b><br><br>%{customdata:.2f}% of %{y} <br><b>Cases</b> %{x:.0}"
            ) for i in range(1,6)
        ])
        #px.bar(self.df,x="continent",y=myDate, color="colorLabel")


        self.fig.update_layout(
            barmode="stack",
            template="plotly_dark",
            width = 888,
            height = 250,
            margin={"r":0, "t":0, "l":0, "b":0},
            showlegend= False,
            paper_bgcolor = "#303030",
            plot_bgcolor = "#303030"
        )

        self.fig.update_xaxes(title_text = "Cases",showgrid=False)
        self.fig.update_yaxes(showgrid=False)


        return self.fig
 

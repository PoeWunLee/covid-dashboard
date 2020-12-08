#this class stores the required x and y axes for the bubble graph
import pandas as pd
from datetime import date
import re
import configparser
import json
from pandas.io.json import json_normalize
from flatten_json import flatten
from datetime import date, datetime, timedelta

class dfFilter:

    def __init__(self,df,myDate):
        self.df = df.copy()
        self.myDate = myDate
        self.nameDict = {
            "confirmed":"new_cases",
            "deaths":"new_deaths",
            "recovered": "new_recovered",
            "active": "new_active"
        }
        self.dailyVarDict = {
            "confirmed-option": "new_cases",
            "deaths-option": "new_deaths",
            "recovered-option":"new_recovered",
            "active-option": "new_active",
        }


    def filter_province_element(self,x):
        if not pd.isnull(x):
            x = "{}, ".format(x)
    
        return x

    def basic_cleaning(self):
        #1) create geoDF and merge
        geoDF = pd.read_csv("https://raw.githubusercontent.com/PoeWunLee/covid-dashboard/main/country_data.csv")[["Province/State","Country/Region","population","population_density","continent"]]
        self.df = self.df.merge(geoDF)

        #2) format province,country name
        #2a) if not NaN, add ", "
        self.df["Province/State"] = self.df["Province/State"].apply(self.filter_province_element)

        #drop all empty continent
        self.df["continent"].dropna(inplace=True)

        #2b) locate NaN and fill with empty string
        self.df["Province/State"].fillna(value="",inplace=True)

        #2c) add to finalise names
        self.df["Name"] = self.df["Province/State"] + self.df["Country/Region"]
        

    def filter_world(self):
        
        self.basic_cleaning()
        

        #3) get relevant date
        self.df = self.df[["Name","Lat","Long", self.myDate,"status","population","population_density","continent"]]

        #4) rename date to "data"
        self.df.rename(columns={self.myDate:"data"},inplace=True)

        #5) fill na with 0
        self.df.fillna(value=0,inplace=True)

        #filter 0 populatio data (i.e. no pop data available)
        self.df = self.df.loc[self.df["population"]!=0]
        self.df.replace(to_replace="",value=0,inplace=True)

        

        return self.df

    def format_value(self,num, newMode=True): 
        resStr = ""

        #first check value
        if num // (10**6) >= 1:
            resStr = "{} Mil".format(round(num/10**6,2))
        elif num//(10000) >=1:
            resStr =  "{}k".format(int(num//1000))
        else:
            resStr = str(int(num))

        #second check if new and +ve or -ve
        if newMode and num>=0:
            resStr = "+{}".format(resStr)
        
        return resStr
        
    
    def filter_total(self):

        totalList, newList = [], []

        for key,value in self.nameDict.items():
            tempDF1 = self.df.loc[(self.df["status"] == key)]
            totalList.append(self.format_value(tempDF1.sum()[self.myDate], newMode=False))
            
            tempDF2 = self.df.loc[(self.df["status"] == value)]
            newList.append(self.format_value(tempDF2.sum()[self.myDate]))
            

        return totalList, newList
    
    def filter_daily(self, myVar):
        
        #basic data cleaning and columns assignment
        self.basic_cleaning()

        #get all relevant dates
        start,end = datetime(2020,1,22), self.myDate
        daycount = (end-start).days+1
        dateList = [(start + timedelta(i)).strftime("%Y-%m-%d") for i in range(daycount)]
        self.df = self.df[dateList + ["status"]]    

        #sum all columns and rename index when converted from Series to DF
        ##using dictionary to identify input and cleaned table status
        self.df = self.df.loc[self.df["status"] == self.dailyVarDict[myVar]].sum().reset_index()

        

        #get 7 day moving average
        ##drop last row of 'status' first
        self.df.drop(self.df.tail(1).index,inplace=True)
        self.df["7 day average"] = self.df[0].rolling(window=7).mean()

        self.df.rename(columns={"index":"date",0:self.dailyVarDict[myVar].replace("_"," ")}, inplace=True)
        

        return self.df


   
    def filter_top_five(self,status):
        
        #basic cleaning of column names
        self.basic_cleaning()

        #group by continent and get top 5
        self.df = self.df.loc[self.df["status"]==self.dailyVarDict[status]]
        
        temp = self.df.copy()[["Province/State","Country/Region",self.myDate, "status","continent","Name"]]
        

        #calculate percentage
        #percentage in world
        temp["percent_world"] = temp[self.myDate]*100 / temp[self.myDate].sum()
       
        #percentage continent
        temp1= temp.copy().groupby(['continent', 'Name']).agg({self.myDate: 'sum'})
        # Change: groupby continent and divide by sum
        temp2 = temp1.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))
        temp2.sort_values(["Name"],inplace=True)
        temp2.rename(columns={self.myDate:"percent_continent"},inplace=True)
        
        
        temp=pd.merge(temp,temp2,on="Name")
        temp = temp.groupby(["continent"]).apply(lambda x: x.sort_values([self.myDate], ascending = False)).reset_index(drop=True)
        
        #get top 5 for each continent
        temp = temp.groupby("continent").head(5)
        temp.reset_index(drop=True,inplace=True)

        #get ranking for figure plotting purposes
        n= len(temp["continent"].unique())
        thisDict = pd.DataFrame({"colorLabel": [i for i in range(5)]*n})
        temp["colorLabel"]  = thisDict

        return temp

        




    




        




    

        

        

        
    


        
        
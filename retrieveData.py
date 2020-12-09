import configparser
import pandas as pd
import dask.dataframe as dd
from datetime import datetime, date,timedelta

class retrieveData:

    def __init__(self,configDict):
        self.configDict = configDict
        self.token = None
        self.response=None
        self.lastUpdate=None
    
    
    def get_token(self,item):
        config = configparser.ConfigParser()
        config.read("config.ini")
        token = config[item][self.configDict[item]]

        return token
    
    def get_all_token(self):
        self.token = {keys:self.get_token(keys) for keys in self.configDict.keys()}
        return self.token
    
    def last_updated(self,df):
        self.lastUpdate = datetime.strptime(df.columns[-1]+"20","%m/%d/%Y")

        return self.lastUpdate
        
    
    def format_date_cols(self,df):

        start,end = datetime(2020,1,22), self.lastUpdate
        daycount = (end-start).days
        dateList = {df.columns[i+4]:(start + timedelta(i)).strftime("%Y-%m-%d") for i in range(daycount+1)}
        
        return df.rename(columns=dateList, inplace=True)
    
    def get_new_status(self,df):
        start,end = datetime(2020,1,22), self.lastUpdate

        daycount = (end-start).days

        dateList = [(start + timedelta(i)).strftime("%Y-%m-%d") for i in range(daycount+1)]
        
        nameDict = {
                "confirmed":"new_cases",
                "deaths":"new_deaths",
                "recovered": "new_recovered",
                "active": "new_active"
            }
        
        dfCopy = df.copy()
        
        for key,value in nameDict.items():
            temp = dfCopy.loc[dfCopy["status"]==key].copy()
            temp[dateList] = temp[dateList].diff(axis=1)
            temp["status"] = value
            dfCopy = pd.concat([dfCopy,temp])
        
        return dfCopy
    
    def get_all_covid_csv(self):

        df1 = dd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
        df2 = dd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
        df3 = dd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

        df1, df2, df3 = df1.compute(), df2.compute(), df3.compute()

        df4, cols = df1.copy(), df1.columns
        df4[cols[4::]] = df4[cols[4::]] - df2[cols[4::]] - df3[cols[4::]]

        #get last updated time
        self.last_updated(df1)
        
        df1["status"], df2["status"], df3["status"], df4["status"] = "confirmed", "deaths", "recovered", "active"
        frames = [df1,df2,df3,df4]

        allDF = pd.concat(frames)
        self.format_date_cols(allDF)
        

        return self.get_new_status(allDF)

    







        
        

                
    



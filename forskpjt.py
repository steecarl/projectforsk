import pandas as pd
import webbrowser
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
import plotly.express as px
from dash.exceptions import PreventUpdate


app=dash.Dash()   #as it is an app

def load_data():    #loads the data
    pd.options.mode.chained_assignment = None  #ignores 
    
    data="global_terror.csv"   #file name
    global df1
    df1=pd.read_csv(data)   #only reads the dataset name 
    
    month={
        "January":1,
         "February": 2,
         "March": 3,
         "April":4,
         "May":5,
         "June":6,
         "July": 7,
         "August":8,
         "September":9,
         "October":10,
         "November":11,
         "December":12
        }
    #to form the values and assort it to dict like values
    global month_list
    month_list=[{"label":key,"value":value}for key,value in month.items()]
    
    global date_list
    date_list=[d for d in range(1,32)]
   
    global region_list
    region_list=[{"label":str(i),"value":str(i)}for i in sorted(df1["region_txt"].unique().tolist())]
    
    global country_list 
    country_list=df1.groupby("region_txt")["country_txt"].unique().apply(list).to_dict()
    
    global state_list
    state_list=df1.groupby("country_txt")["provstate"].unique().apply(list).to_dict()
    
    global city_list
    city_list=df1.groupby("provstate")["city"].unique().apply(list).to_dict()
    
    global attack_type_list
    attack_type_list = [{"label": str(i), "value": str(i)}  for i in df1['attacktype1_txt'].unique().tolist()]
    
    
    global year_list
    year_list=sorted(df1["iyear"].unique().tolist())
    
    global year_dict
    year_dict={str(year):str(year)for year in year_list}
    
    chartC={"Terrorist Organisation":'gname',
           "Target Nationality":'natlty1_txt',
           "Target Type":'targtype1_txt',
           "Type of Attack":'attacktype1_txt',
           "Weapon Type":'weaptype1_txt',
           "Region":'region_txt',
           "Country Attacked":'country_txt'}
    global chart_dropdown 
    chart_dropdown=[{"label":keys,"value":value}for keys,value in chartC.items()]
        
def create_ui():#creates the face of your app
    main_layout=html.Div([
        html.H1(children="Terrorism analysis and Insights",id="main_title"),
        dcc.Tabs(id="Tabs",value="map", children=[
            dcc.Tab(label="Map tool",id="map_tool",value="map",children=[
                dcc.Tabs(id="subtabs",value="worldM",children=[
                        dcc.Tab(label="world map",id="world_map",value="worldM"),
                        dcc.Tab(label="india map",id="india_map",value="indiaM")]),
                 dcc.Dropdown(        #to form dropdown bar
                      id='dropdown_month', 
                      options=month_list,
                      placeholder='Select Month',
                      multi = True
                ),
                dcc.Dropdown(
                      id='dropdown_date', 
                      placeholder='Select Day',
                      multi = True
                ),
                dcc.Dropdown(
                      id='dropdown_region', 
                      options=region_list,
                      placeholder='Select Region',
                      multi = True
                ),
                dcc.Dropdown(
                      id='dropdown_country', 
                      options=[{'label': 'All', 'value': 'All'}],
                      placeholder='Select Country',
                      multi = True
                ),
                dcc.Dropdown(
                      id='dropdown_state', 
                      options=[{'label': 'All', 'value': 'All'}],
                      placeholder='Select State or Province',
                      multi = True
                ),
                dcc.Dropdown(
                      id='dropdown_city', 
                      options=[{'label': 'All', 'value': 'All'}],
                      placeholder='Select City',
                      multi = True
                ),
                dcc.Dropdown(
                      id='dropdown_attacktype', 
                      options=attack_type_list,#[{'label': 'All', 'value': 'All'}],
                      placeholder='Select Attack Type',
                      multi = True
                ),
              
                html.H5('Select the Year', id='year_title'),
                dcc.RangeSlider(     #to form range slider
                      id='year-slider',
                      min=min(year_list),
                      max=max(year_list),
                      value=[min(year_list),max(year_list)],
                      marks=year_dict,
                      step=None
                ),
                ]),
        
            dcc.Tab(label="chart tool",id="chart",value="chart",children=[
                dcc.Tabs(id="subtabs2",value="worldC",children=[
                        dcc.Tab(label="world map",id="world_map2",value="worldC"),
                        dcc.Tab(label="india map",id="india_map2",value="indiaC")]),
                        html.Br(),
                        
                                    dcc.Dropdown(id="chart_drop",
                                     options=chart_dropdown,
                                     placeholder="select category",
                                     value="region_txt"),
                                  html.Br(),
                                  html.Hr(),
                                  dcc.Input(id="search", placeholder="Search Filter"),
                                  html.Hr(),
                        dcc.RangeSlider(
                            id="cyear-slider",
                            min=min(year_list),
                            max=max(year_list),
                            value=[min(year_list),max(year_list)],
                            marks=year_dict,
                            step=None
                            
                            ),
                        
            ])
            ]),
                        
    html.Div(id="graph-object",children="graph is loading")
    ])
        
            
    return main_layout

@app.callback(
    dash.dependencies.Output("graph-object","children"),
    [
    dash.dependencies.Input("dropdown_month","value"),  #for the map tool part
    dash.dependencies.Input("dropdown_date","value"),
    dash.dependencies.Input("dropdown_region","value"),
    dash.dependencies.Input("dropdown_country","value"),
    dash.dependencies.Input("dropdown_state","value"),
    dash.dependencies.Input("dropdown_city","value"),
    dash.dependencies.Input("dropdown_attacktype","value"),
    dash.dependencies.Input("year-slider","value"),
    dash.dependencies.Input("subtabs2","value"),   #for the chart tool part
    dash.dependencies.Input("search","value"),
    dash.dependencies.Input("cyear-slider","value"),
    dash.dependencies.Input("chart_drop","value"),
    dash.dependencies.Input("Tabs","value"),
    
    ])  
def update_graph_ui(month,date,region,country,state,city,attacktype,year_slider,sb2,s_filter,cyear,dropC,Tab):  #changes observed when the value is selected
    fig=None #by default
    
    if Tab=="map":  #to execute the map part 
        
        print("the data type is "+str(type(month)))
        print("the month selected is "+str(month))
        
        
        print("the data type is "+str(type(date)))
        print("the date selected is "+str(date))
       
        print("the data type is "+str(type(region)))
        print("the country selected is "+str(region))
        
        print("the data type is "+str(type(country)))
        print("the region selected is "+str(country))
        
        
        print("the data type is "+str(type(state)))
        print("the state selected is "+str(state))
        
        print("the data type is "+str(type(city)))
        print("the city selected is "+str(city))
        
        print("the data type is "+str(type(attacktype)))
        print("the attacktype selected is "+str(attacktype))
        
        print("the data type is "+str(type(year_slider)))
        print("the year selected is "+str(year_slider))
        
        year_range=range(year_slider[0],year_slider[1]+1)
        new_df=df1[df1["iyear"].isin(year_range)]
    
        if month==[] or month is None:
            pass
        else:
            if date==[] or date is None:
                new_df=new_df[new_df["imonth"].isin(month)]
            else:
                new_df=new_df[(new_df["imonth"].isin(month)) & 
                              (new_df["iday"].isin(date))]
            
    
        if region==[] or region is None:
            pass
        else:
            if country==[] or country is None:
                new_df=new_df[new_df["region_txt"].isin(region)]
            else:
                if state==[] or state is None:
                    new_df=new_df[(new_df["region_txt"].isin(region)) & (new_df["country_txt"].isin(country))]
            
                else:
                    if city==[] or city is None:
                        new_df=new_df[(new_df["region_txt"].isin(region)) & (new_df["country_txt"].isin(country)) & (new_df["provstate"].isin(state))]
                    else:
                        new_df=new_df[(new_df["region_txt"].isin(region)) & (new_df["country_txt"].isin(country)) & (new_df["provstate"].isin(state)) & (new_df["city"].isin(city))]
                    
        if attacktype is None:
            pass
        else:
            new_df=new_df[new_df["attacktype1_txt"].isin(attacktype)]
            mapfigure=go.Figure()
        
        if new_df.shape[0]:
            pass
        else: 
            new_df = pd.DataFrame(columns = ['iyear', 'imonth', 'iday', 'country_txt', 'region_txt', 'provstate',
                   'city', 'latitude', 'longitude', 'attacktype1_txt', 'nkill'])
                    
            new_df.loc[0] = [0, 0 ,0, None, None, None, None, None, None, None, None]
            
    
        mapfigure=px.scatter_mapbox(new_df,
                             lat="latitude",
                             lon="longitude",
                             hover_data=["region_txt","country_txt","city","provstate","iyear"],
                             color="attacktype1_txt",
                             zoom=1
                             )
        mapfigure.update_layout(mapbox_style="stamen-toner",
                         autosize=True,
                         margin=dict(l=0,r=0,t=30,b=30),
                         )
        fig=mapfigure
    elif Tab=="chart":
        fig=None
        
        cyear_slider=range(cyear[0],cyear[1]+1)
        chart_df=df1[df1["iyear"].isin(cyear_slider)]
            
        if sb2=="worldC":
            pass
        elif sb2=="indiaC":
            chart_df=chart_df[(chart_df["region_txt"]=="South Asia") & (chart_df["country_txt"]=="India")]
            
        if dropC is not None and chart_df.shape[0]:
            if s_filter is not None:
            
                chart_df=chart_df.groupby("iyear")[dropC].value_counts().reset_index(name="count")
                chart_df=chart_df[chart_df[dropC].str.contains(s_filter,case=False)]
            else:
                chart_df=chart_df.groupby("iyear")[dropC].value_counts().reset_index(name="count")
        else:
                raise PreventUpdate
                
        if chart_df.shape[0]:
            pass
        else: 
            chart_df = pd.DataFrame(columns = ['iyear', 'count', dropC])
            chart_df.loc[0] = [0, 0,"No data"]
            
                
        fig = px.area(chart_df, x= "iyear", y ="count", color = dropC)
    else:
          return None
    
    return dcc.Graph(figure=fig)




@app.callback(
    Output("dropdown_date","options"),
    [
    Input("dropdown_month","value")
    ]
    )
def update_date(month):
    option=[]
    if month:
        option=[{"label":m,"value":m}for m in date_list]
    return option
@app.callback([Output("dropdown_region", "value"),
               Output("dropdown_region", "disabled"),
               Output("dropdown_country", "value"),
               Output("dropdown_country", "disabled")],
              [Input("subtabs", "value")])
def update_r(tab):
    region = None
    disabled_r = False
    country = None
    disabled_c = False
    if tab == "worldM":
        pass
    elif tab =="indiaM":
        region = ["South Asia"]
        disabled_r = True
        country = ["India"]
        disabled_c = True
    return region, disabled_r, country, disabled_c
    
@app.callback(
    Output("dropdown_country","options"),
    [
    Input("dropdown_region","value")
    ]
    )  
def country(region):
    option=[]
    if region is None:
        raise PreventUpdate
    else:
        for var in region:
            if var in country_list.keys():
                option.extend(country_list[var])
    return [{'label':m , 'value':m} for m in option]
@app.callback(
    Output("dropdown_state","options"),
    [
    Input("dropdown_country","value")
    ]
    )  
def state(country):
    option=[]
    if country is None:
        raise PreventUpdate
    else:
        for var in country:
            if var in state_list.keys():
                option.extend(state_list[var])
    return[{"label":m,"value":m}for m in option]

@app.callback(
    Output("dropdown_city","options"),
    [
    Input("dropdown_state","value")
    ]
    )  
def state(state):
    option=[]
    if state is None:
        raise PreventUpdate
    else:
        for var in state:
            if var in city_list.keys():
                option.extend(city_list[var])
    return[{"label":m,"value":m}for m in option]       
        

def webbrowser_open():
    webbrowser.open_new('http://127.0.0.1:8050/')
    

def main():
    load_data()
    webbrowser_open()
    global app
    app.layout=create_ui()
    app.title="Terrorism analysis and Insights"
    app.run_server()    
    app=None
    df1=None
    
    
if __name__ =="__main__":
    print("the program is going to start")
    main()
    print("the program has been ended")
    
    


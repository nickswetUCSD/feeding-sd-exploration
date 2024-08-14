# explorefuncs.py
#
# A library of functions to be used in explore.py, a script which runs these functions in sequence.
# Contains: read_file, clean_data, hours_plot TODO
#
#
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from urllib.request import urlopen


def read_file(file_path):
    return pd.read_csv(file_path, low_memory = False)

def clean_data(df):
    '''Takes valuable columns, copies data to new dataframe, and cleans accordingly.'''
    
    keepCols = ['User ID',
                'Opportunity City',
                'Opportunity State',
                'Opportunity Zip',
                'Date of Birth',
                'Date',
                'Time',
                'End Date',
                'End Time',
                'Hours',
                'Languages Spoken',
                'Public Gender'
                ]
    df = (df[keepCols]).copy()
    
    # Cleaning time data
    df['Start Date'] = df['Date']
    df['End Date'] = df['End Date']
    df['Start Time'] = df['Time']
    df['End Time'] = df['End Time']
    daynames = {0: 'Monday',
                1: 'Tuesday',
                2: 'Wednesday',
                3: 'Thursday',
                4: 'Friday',
                5: 'Saturday',
                6: 'Sunday'}

    df['Weekday'] = df['Start Date'].apply(lambda x: daynames[pd.Timestamp(x).day_of_week])
    df = df.drop(columns=['Date', 'Time'])
    
    # Extra care for data entry errors (recognized by large numbers of entries at a single date);
    # Example from 2023: should drop ~14000 rows with faulty time data entry (July 1st, 2022).
    counts = df.groupby('Start Date')['User ID'].count()
    to_exclude = counts[counts > 5000].index
    df = df[df['Start Date'].apply(lambda x: False if x in to_exclude else True)]
        
    # Additionally drops rows without entries for 'Start Date', 'Start Time', 'Opportunity Zip'
    df = df[~df['Start Date'].isna()]
    df = df[~df['Start Time'].isna()]
    df = df[~df['Opportunity Zip'].isna()]
    
    # Corrects faulty 'Hours' entries IF the entry is smaller than what is calculated by Start and End times.
    df['Start'] = pd.to_datetime(df['Start Date'] + ' ' + df['Start Time'])
    df['End'] = pd.to_datetime(df['End Date'] + ' ' + df['End Time'])
    df['Calculated Hours'] = (df['End'] - df['Start']).apply(lambda t: t.seconds / 3600)

    return df



def hoursPlot(df, out_dir, raw=False):
    '''Creates histogram of Hours from cleaned DataFrame. Implicitly cleans Hours: No hour values greater than 24 hours considered. 
    All 0 hour sessions replaced with manual calculation of their session length.
    Setting raw=True ignores this cleaning.'''
    
    if raw:
        replacedHours = df['Hours']
    else:
        df = df[df['Hours'] <= 24]
        whereZero = (df['Hours'] == 0)
        replacedHours = (df['Hours']) + (df['Calculated Hours'] * whereZero) 
    
    fig = px.histogram(replacedHours, nbins = 24)
    fig.update_xaxes(nticks=24)
    fig.update_layout(
        title_text='Distribution of Volunteer Session Lengths (Hours)', # title of plot
        xaxis_title_text='Volunteer Session Length (Hours)', # xaxis label
        yaxis_title_text='Count of Sessions', # yaxis label
        showlegend = False
    )
    out_path = os.path.join(out_dir, "hours-distribution.html")
    fig.write_html(out_path), print('Plot 1/4 Created...')
    

def weektimeHeatmap(df, out_dir):
    '''Takes in a cleaned dataframe from timePlotsSetUp to produce a heatmap.
    Heatmap colors average volunteer participation across time of day per day of the week.'''

    def floor_hour(s):
        '''Takes a string time of the format 'XX:XX (A/P)M', returns hour of day as int in military time. 
        Faster than pd.datetime methods for our purposes. '''
        t = (int(s[:-6])) * 100 + int(s[-5:-3])
        if (s[:2] == '12'):
            t += 1200
        if s[-2] == 'P':
            t += 1200
        return (t % 2400) // 100

    df['Time of Day'] = df['Start Time'].apply(floor_hour).apply(lambda x: (x // 4) * 4).sort_values(ascending=False)
    vals = (df.pivot_table(index='Weekday', columns='Time of Day', values='User ID', aggfunc='count', fill_value=0).T)/52
    vals = vals[['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']]
    fig = px.imshow(vals, 
              labels=dict(x="Day of Week", y="Time of Day", color="Average Volunteer Arrivals"),
              x=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 
              y=['12 AM', '4 AM', '8 AM', '12 PM', '4 PM', '8 PM'],
              color_continuous_scale=[(0, "#F7F4EA"), (0.5, "#DD757E"), (1, "#db2b39")],
              title = 'Average Distribution of Volunteer Participation (Week View)',
             )
    out_path = os.path.join(out_dir, "weektime-heatmap.html")
    fig.write_html(out_path),  print('Plot 2/4 Created...')

def participationYear(df, out_dir):
    '''Takes in a cleaned dataframe from timePlotsSetUp.
    Returns a 12-month faceted line plot, one graph for volunteer participation per each month.'''

    months = {1: 'January',
              2: 'February',
              3: 'March',
              4: 'April',
              5: 'May',
              6: 'June',
              7: 'July',
              8: 'August',
              9: 'September',
              10: 'October',
              11: 'November',
              12: 'December'
             }

    df = df.groupby('Start Date')['User ID'].count().reset_index()
    df['Day'] = df['Start Date'].apply(lambda s: pd.to_datetime(s).day)
    df['Month'] = df['Start Date'].apply(lambda s: int(s[:2]) if s[1] != '/' else int(s[0]))
    df = df.sort_values(by = ['Month','Day'], ascending = True)
    df['Month'] = df['Month'].apply(lambda m: months[m])

    df = df.rename(columns={'User ID': 'Volunteers'})

    # MONTHLY TABLE
    # print(df.groupby('Month')['Volunteers'].mean())

    # YEARLY AVERAGE
    # y = df.groupby('Month')['Volunteers'].sum().sum() / df.shape[0]

    fig = px.line(df, x="Day", y="Volunteers", facet_col="Month", facet_col_wrap=4)
    fig.update_layout(
        title_text='Number of Daily Volunteers Across The Year (Red Line Is Year Average)', # title of plot

    )
    fig.add_hline(y = df.groupby('Month')['Volunteers'].sum().sum() / df.shape[0], line_dash="dot",
              annotation_text="",
              annotation_position="bottom right", 
              line_color = 'red',
              )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_traces(line_color='#064789')
    out_path = os.path.join(out_dir, "participation-by-year.html")
    fig.write_html(out_path),  print('Plot 3/4 Created...')
    
    
def locationPlot(df, out_dir):
    '''Returns a choropleth location plot where zip code regions are colored based on total daily volunteers.
    NotYetImplemented: Month argument takes any name of a month in strict lowercase (ex: 'january', 'october' ...) 
    OR 'all' for data to be considered across all twelve months.'''
    
    df = df.copy()
    
    geodata_url = 'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/ca_california_zip_codes_geo.min.json'
    with urlopen(geodata_url) as response:
        counties = json.load(response)
    
    df = df.groupby('Opportunity Zip')['User ID'].count().reset_index()
    df['Log Users'] = np.log(df['User ID'])
    
    fig = px.choropleth(df, geojson=counties, locations='Opportunity Zip', color='Log Users', 
                           featureidkey="properties.ZCTA5CE10",
                           color_continuous_scale=[(0, "#F7F4EA"), (0.5, "#DD757E"), (1, "#db2b39")],
                           scope="usa",
                           labels={'Log Users':'Log of Total Daily Volunteers'}
                          )
    out_path = os.path.join(out_dir, "location-popularity.html")
    fig.write_html(out_path),  print('Plot 4/4 Created...')
    
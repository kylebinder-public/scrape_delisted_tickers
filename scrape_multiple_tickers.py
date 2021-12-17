# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 21:56:46 2021
@author: Kyle
"""

from selenium import webdriver # needed to pip install
import time
import datetime
import pandas as pd
import csv
import os


#############################
# INPUTS:
#############################

cwd = os.getcwd()
#csv_to_write = r'C:\Users\Kyle\Desktop\_FOLDERS_\__DATASETS\Delisted_Tickers\scraper_outputs_0004n.csv'
csv_to_write = cwd + str('\scraper_outputs_small.csv')

#csv_to_read = r'C:\Users\Kyle\Desktop\_FOLDERS_\__DATASETS\Delisted_Tickers\scraper_inputs_all_to_mod_mid_runs_04.csv'
csv_to_read = cwd + str('\scraper_inputs_small.csv')
df_inputs = pd.read_csv(csv_to_read)

for rr in range(0, df_inputs.shape[0]):

    ticker_str = str(df_inputs.iloc[rr,0])
    dates_first = datetime.date(df_inputs.iloc[rr,1], df_inputs.iloc[rr,2], df_inputs.iloc[rr,3])
    dates_last = datetime.date(df_inputs.iloc[rr,4], df_inputs.iloc[rr,5], df_inputs.iloc[rr,6])

    #############################
    # GO:
    #############################
    
    print(datetime.datetime.now())
    print(str('----------------------------'))
    
    # Pad with leading zeroes version needed - ex: '01' for January
    dates_array = pd.date_range(dates_first, dates_last, freq='D')
#    dates_df_leading_zeroes = pd.DataFrame(columns=['year','month','day'],index=dates_array,dtype=[object,object,object])
    dates_df_leading_zeroes = pd.DataFrame(columns=['year','month','day'],dtype=object)
    print('Creating date array')
    for rr in range(0, dates_df_leading_zeroes.shape[0]):
        dates_df_leading_zeroes.iloc[rr,0] = str(dates_array[rr].year)
        if dates_array[rr].month < 10:
            dates_df_leading_zeroes.iloc[rr,1] = str('0')+str(dates_array[rr].month)
        else:
            dates_df_leading_zeroes.iloc[rr,1] = str(dates_array[rr].month)
        if dates_array[rr].day < 10:
            dates_df_leading_zeroes.iloc[rr,2] = str('0')+str(dates_array[rr].day)  
        else:
            dates_df_leading_zeroes.iloc[rr,2] = str(dates_array[rr].day) 
            
    # Version without leading zeros, used for writing dates with no data to CSV:
    dates_df = pd.DataFrame(columns=['year','month','day'],index=dates_array)
    for rr in range(0, dates_df.shape[0]):
        dates_df.iloc[rr,0] = dates_array[rr].year
        dates_df.iloc[rr,1] = dates_array[rr].month
        dates_df.iloc[rr,2] = dates_array[rr].day
    
    print('Finished creating date array')
    
    # Loop through days; each iteration we make a browser call:
    for rr in range(0, dates_df_leading_zeroes.shape[0]):
        
        # Define substrings of the URL:
        month_str = str(dates_df_leading_zeroes.iloc[rr,1])
        day_str = str(dates_df_leading_zeroes.iloc[rr,2])
        year_str = str(dates_df_leading_zeroes.iloc[rr,0])
        
        print(str('----------------------------'))
        print(str('Browser call ')+str(ticker_str)+\
            str(' month=')+\
            str(month_str)+\
            str(' day=')+\
            str(day_str)+\
            str(' year=')+\
            str(year_str))
        print(datetime.datetime.now())
        
        browser = webdriver.Firefox()
        browser.set_window_size(300,300)
          
        url = str('https://www.historicalstockprice.com/history/?a=historical&ticker=')+\
            str(ticker_str)+\
            str('&month=')+\
            str(month_str)+\
            str('&day=')+\
            str(day_str)+\
            str('&year=')+\
            str(year_str)+\
            str('&x=13&y=8')
        
        # Example of URL that gets created:
        #url = 'https://www.historicalstockprice.com/history/?a=historical&ticker=AABA&month=01&day=12&year=2001&x=13&y=8'
        
        browser.get(url)
        time.sleep(6)
        html = browser.execute_script('return document.documentElement.outerHTML')
        
        # Get substring of java-executed HTML that contains our desried fields:
        html_startpoint = html.find('Volume')
        html_endpoint = html[html_startpoint:].find('</tbody></table>')
        
        # If string "Volume" is found, then keep parsing; else, we don't have data 
        # (either weekend or holiday or finally delisted)
        if html_endpoint == -1:
            print(str(' NO DATA FOUND FOR THIS DATE '))
            field_1 = str(dates_array[rr].month) + str('/') + str(dates_array[rr].day) + str('/') + str(dates_array[rr].year)
            # Field 2 of 6: get open:
            field_2 = 'nan'
            # Field 3 of 6: get high:
            field_3 = 'nan'
            # Field 4 of 6: get low:
            field_4 = 'nan'
            # Field 5 of 6: get close:
            field_5 = 'nan'
            # Field 6 of 6: get volume:
            field_6 = 'nan'
        else:
            print(str(' DATA FOUND '))
            substr = html[ html_startpoint : html_startpoint + html_endpoint ]
            
            six_startpoints = [i for i in range(len(substr)) if substr.startswith('<font color="#222222">', i)]
            six_endpoints = [i for i in range(len(substr)) if substr.startswith('</font></td>', i)]
            
            # Field 1 of 6: get date:
            field_1 = substr[six_startpoints[0]+len('<font color="#222222">'):six_endpoints[0]]
            # Field 2 of 6: get open:
            field_2 = substr[six_startpoints[1]+len('<font color="#222222">'):six_endpoints[1]]
            # Field 3 of 6: get high:
            field_3 = substr[six_startpoints[2]+len('<font color="#222222">'):six_endpoints[2]]
            # Field 4 of 6: get low:
            field_4 = substr[six_startpoints[3]+len('<font color="#222222">'):six_endpoints[3]]
            # Field 5 of 6: get close:
            field_5 = substr[six_startpoints[4]+len('<font color="#222222">'):six_endpoints[4]]
            # Field 6 of 6: get volume:
            field_6 = substr[six_startpoints[5]+len('<font color="#222222">'):six_endpoints[5]]
                             
        
        browser.quit()
        
        print(str('Writing to CSV for ')+str(ticker_str)+\
            str(' month=')+\
            str(month_str)+\
            str(' day=')+\
            str(day_str)+\
            str(' year=')+\
            str(year_str))
        
        # Append results to CSV:
        row_to_write = [ field_1 , field_2 , field_3 , field_4 , field_5 , field_6 , ticker_str ]
        with open(csv_to_write, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row_to_write)
        print(str('----------------------------'))
    
print('FINISHED AT: ')
print(datetime.datetime.now())
    
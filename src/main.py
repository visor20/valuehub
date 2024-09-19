# main python module

import settings
from private_settings import PRIVATE_KEY
import requests
import csv
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# financial modeling prep key (unique to user)
api_key = PRIVATE_KEY

def get_openinsider():
    data = pd.DataFrame(columns=settings.KEYS)

    end = datetime.now()
    start = end - timedelta(days=settings.LOOKBACK)
    start_str = start.strftime('%m/%d/%Y')
    end_str = end.strftime('%m/%d/%Y')

    print("start - end: " + start_str + "-" + end_str)
    url = f'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=-1&fdr={start_str}+-+{end_str}&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=5000&page=1'
   
    response = requests.get(url)
    soup =  BeautifulSoup(response.text, 'html.parser')
    
    try:
        rows = soup.find('table', {'class': 'tinytable'}).find('tbody').findAll('tr')
    except:
        print("Error! Skipping")
        logger.error(f"This URL was not successful: {url}")
        return

    for row in rows:
        cols = row.findAll('td')
        if not cols:
            continue
        cur_data = {key: cols[index].find('a').text.strip() if cols[index].find('a') else cols[index].text.strip() 
                        for index, key in enumerate(settings.KEYS)}
        data.loc[len(data)] = cur_data
    return data.drop_duplicates(ignore_index=True)


def drop_columns(df):
    df.drop('X', axis=1, inplace=True)
    df.drop('company_name', axis=1, inplace=True)
    df.drop('trade_type', axis=1, inplace=True)


def filter_data(data):
    filtered = data[data['trade_type'] == 'P - Purchase']
    return filtered.reset_index(drop=True)


def get_ticker_dict(data):
    td = {}
    for i, r in data.iterrows():
        ticker = r['ticker']
        if ticker not in td:
            td[ticker] = 1
        else:
            td[ticker] += 1
    return td


def main():
    data = filter_data(get_openinsider())
    drop_columns(data)
    ticker_dict = get_ticker_dict(data)
    
    df = pd.DataFrame(columns=['ticker', 'num_trades', 'P/E', 'PEG', 'P/B'])
    for t in ticker_dict.items():
        if t[1] >= settings.CLUSTER_VAL:
            url = f'https://financialmodelingprep.com/api/v3/ratios-ttm/{t[0]}?apikey={api_key}'
            response = requests.get(url)
            t_data = response.json()

            # TTM = trailing twelve months
            pe, pb, peg = 0, 0, 0
            if t_data:
                pe = t_data[0]['peRatioTTM']
                pb = t_data[0]['priceToBookRatioTTM']
                peg = t_data[0]['pegRatioTTM']
            df.loc[len(df)] = {'ticker': t[0], 'num_trades': t[1], 'P/E': pe, 'PEG': peg, 'P/B': pb}

    sorted_df = df.sort_values(by='P/E')
    print(sorted_df.reset_index(drop=True))

if __name__ == "__main__":
    main()

import requests
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import settings
from private_settings import FMP_PRIVATE_KEY


# backend flask requires CORS for comm. across ports
app = Flask(__name__)
app.json.sort_keys = False 
CORS(app)


def get_openinsider(lookback: int) -> pd.DataFrame:
    """
    Parameters
    ----------
        lookback (int) - from today, number of days to collect data

    Return
    ------
        pd.DataFrame containing openinsider data
    """
    data = pd.DataFrame(columns=settings.KEYS)
    end = datetime.now()
    start = end - timedelta(days=lookback)
    start_str = start.strftime('%m/%d/%Y')
    end_str = end.strftime('%m/%d/%Y')

    # url (purchase only && trades exceeding 10k)
    url = f'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=-1&fdr={start_str}+-+{end_str}&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=10&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1'
   
    # GET the FMP API data
    response = requests.get(url)
    soup =  BeautifulSoup(response.text, 'html.parser')
    
    try:
        # openinsider table has class="tinytable"
        rows = soup.find('table', {'class': 'tinytable'}).find('tbody').findAll('tr')
    except:
        # logging might be best here...
        print("Cannot access Openinsider table")
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


def get_ticker_dict(data):
    td = {}
    for i, r in data.iterrows():
        ticker = r['ticker']
        if ticker not in td:
            td[ticker] = 1
        else:
            td[ticker] += 1
    return td


def check_for_nulls(r_node, p_node):
    if not r_node or not p_node:
        return False
   
    r_of_interest = ['peRatioTTM', 'priceToBookRatioTTM', 'pegRatioTTM', 'priceToSalesRatioTTM']
    for rv in r_node: 
        if rv in r_of_interest and r_node[rv] == None:
            return False

    p_of_interest = ['price', 'sector', 'mkt_cap']
    for pv in p_node:
        if pv in p_of_interest and p_node[pv] == None:
            return False
    return True


@app.route('/api/stocks', methods=['GET'])
def get_valuehub_data():
    """ 
    Get the open insider and fundamental data.
    
    frontend arguments
    ------------------
        lookback (int), cluster_val (int)

    Return
    ------
        Response Object: Response containing JSON for frontend.
    """
    lookback = request.args.get('lookback', type=int)
    cluster_val = request.args.get('cluster_val', type=int)

    data = get_openinsider(lookback)
    drop_columns(data)
    ticker_dict = get_ticker_dict(data)

    df = pd.DataFrame(columns=['ticker', 'sector', 'price', 'mkt_cap', 'num_trades', 'PS', 'PB', 'PE', 'PEG', 'DCF'])
    for t in ticker_dict.items():
        if t[1] >= cluster_val:
            # TTM == trailing twelve months
            ratios_url = f'https://financialmodelingprep.com/api/v3/ratios-ttm/{t[0]}?apikey={FMP_PRIVATE_KEY}'
            profile_url = f'https://financialmodelingprep.com/api/v3/profile/{t[0]}?apikey={FMP_PRIVATE_KEY}'

            r_data = requests.get(ratios_url).json()
            p_data = requests.get(profile_url).json()
            
            if r_data and p_data:
                r_node = r_data[0]
                p_node = p_data[0]

                if check_for_nulls(r_node, p_node):
                    sector, price, dcf, mkt_cap, ps, pe, pb, peg = 0, 0, 0, 0, 0, 0, 0, 0
                    pe = round(r_node['peRatioTTM'], settings.NUM_DECIMALS)
                    pb = round(r_node['priceToBookRatioTTM'], settings.NUM_DECIMALS)
                    peg = round(r_node['pegRatioTTM'], settings.NUM_DECIMALS)
                    ps = round(r_node['priceToSalesRatioTTM'], settings.NUM_DECIMALS)
                    sector = p_node['sector']
                    price = p_node['price']
                    dcf = round(p_node['dcf'], settings.NUM_DECIMALS)
                    mkt_cap = int(p_node['mktCap'] / settings.MKT_CAP_MULT) # puts it in millions
                    df.loc[len(df)] = ({'ticker': t[0], 'sector': sector,
                                    'price': price, 'mkt_cap': mkt_cap,
                                    'num_trades': t[1], 'PS': ps, 'PB': pb,
                                    'PE': pe, 'PEG': peg, 'DCF': dcf})

    sorted_df = df.sort_values(by='PE')
    sorted_df.reset_index(drop=True, inplace=True)

    # debug tool
    if settings.PRINT_TOGGLE:
        print(sorted_df)
    return jsonify(sorted_df.to_dict(orient='index'))


if __name__ == "__main__":
    app.run(debug=True)



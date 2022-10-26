# Import libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

# Scraping
# HTTP Request
# store website in variable
website = "https://www.coingecko.com/"
response = requests.get(website)

# status code
# print(response)

# Soup Object
soup = BeautifulSoup(response.content, 'html.parser')
# print(soup)

# Results
# starting point
results = soup.find('table', {'class': 'table-scrollable'}).find('tbody').find_all('tr')
# print(len(results))

# Find your Data
# symbol
# symbol = results[0].find('a', {'class': 'tw-flex tw-items-start md:tw-flex-row tw-flex-col'}).find_all('span')[1].get_text().strip()
# print(symbol)

# name
# name = results[0].find('a', {'class': 'tw-flex tw-items-start md:tw-flex-row tw-flex-col'}).find_all('span')[0].get_text().strip()
# print(name)

# price
# price = results[0].find('td', {'class': 'td-price'}).get_text().strip().split('$')[1]
# print(price)

# % change
# change = results[0].find('td', {'class': 'td-change24h'}).get_text().strip()
# print(change)

# market_cap
# market_cap = results[0].find('td', {'class': 'td-market_cap'}).get_text().strip()
# print(market_cap)

# Put everything together - For Loop
symbol_list = []
name_list = []
price_list = []
change_list = []
mcap_list = []

for i in results:

    # symbol
    symbol_list.append(i.find('a', {'class': 'tw-flex tw-items-start md:tw-flex-row tw-flex-col'}).find_all('span')[1].get_text().strip())

    # name
    name_list.append(i.find('a', {'class': 'tw-flex tw-items-start md:tw-flex-row tw-flex-col'}).find_all('span')[0].get_text().strip())

    # price
    price_list.append(i.find('td', {'class': 'td-price'}).get_text().strip().split('$')[1])

    # % change
    change_list.append(i.find('td', {'class': 'td-change24h'}).get_text().strip())

    # market cap
    mcap_list.append(i.find('td', {'class': 'td-market_cap'}).get_text().strip())

# Pandas Dataframe
df_scrape = pd.DataFrame({'Symbol': symbol_list, 'Name': name_list, 'Price': price_list,
                       '% Change': change_list, 'Market Cap': mcap_list})

df_scrape['% Change'] = df_scrape['% Change'].str.replace("%","")
df_scrape['% Change'] = df_scrape['% Change'].astype(float)

# print(df_scrape.info())


#------------------------------------------
# Streamlit Integration
import streamlit as st

st.set_page_config(layout="wide")
# -------------------
# Streamlit Sidebar
# -------------------
fiat = ['USD', 'EUR', 'GBP']
tokens = df_scrape.Symbol.values
# filters selectbox
st.sidebar.title("Filters")
select_token = st.sidebar.selectbox('Tokens', tokens)
select_fiat = st.sidebar.selectbox('Fiat', fiat)
# special expander objects
st.sidebar.markdown('***')
with st.sidebar.expander('Help'):
    st.markdown('''
                    - Select token and fiat of your choice.
                    - Interactive plots can be zoomed or hovered to retrieve more info.
                    - Plots can be downloaded using Plotly tools.''')
# -------------------
# Title Image
# -------------------
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    st.write("")
with col2:
    st.image('title.png', width=700)
with col3:
    st.write("")

st.markdown('***')
# -------------------
# Add crypto logo and name
# -------------------
col1, col2 = st.columns([1, 10])
with col1:
    try:
        st.image('bitcoin-btc-logo.png', width=70)
    except:
        pass
with col2:
    st.markdown(f'''## {select_token}''')


#------------------------------------------
# Candlestick chart
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# download 5 year crypto prices from Yahoo Finance
df = yf.download(tickers='BTC-USD', period='5y', interval='1d')
# compute moving averages
df['MA100'] = df.Close.rolling(100).mean()
df['MA50'] = df.Close.rolling(50).mean()
df['MA20'] = df.Close.rolling(20).mean()
# Plotly candlestick chart
fig = go.Figure(data=
                [go.Candlestick(x=df.index,
                                open=df.Open,
                                high=df.High,
                                low=df.Low,
                                close=df.Close,
                                name=f'{select_token}'),
                 go.Scatter(x=df.index, y=df.MA20,
                            line=dict(color='yellow', width=1), name='MA20'),
                 go.Scatter(x=df.index, y=df.MA50,
                            line=dict(color='green', width=1), name='MA50'),
                 go.Scatter(x=df.index, y=df.MA100,
                            line=dict(color='red', width=1), name='MA100')])

fig.update_layout(go.Layout(xaxis={'showgrid': False},
                            yaxis={'showgrid': False}),
                  title=f'{select_token} Price Fluctuation with Moving Averages',
                  yaxis_title=f'Price ({select_fiat})',
                  xaxis_rangeslider_visible=False)

# -------------------
# Candlestick chart with moving averages
# -------------------
st.plotly_chart(fig, use_container_width=True)
# -------------------


#------------------------------------------
# Daily Trends Line Chart
# download daily crypto prices from Yahoo Finance
df = yf.download(tickers=f'{select_token}-{select_fiat}', period = '1d', interval = '1m')
# Plotly line chart
fig = go.Figure()
fig.add_scattergl(x=df.index, y=df.Close,
                  line={'color': 'green'},name='Up trend')
fig.add_scattergl(x=df.index, y=df.Close.where(df.Close <= df.Open[0]),
                  line={'color': 'red'},name='Down trend')
fig.add_hline(y=df.Open[0])
fig.update_layout(go.Layout(xaxis = {'showgrid': False},
                  yaxis = {'showgrid': False}),
                  title=f'{select_token} Daily Trends in Comparison to Open Price',
                    yaxis_title=f'Price ({select_fiat})',template='plotly_dark',
                    xaxis_rangeslider_visible=False)

# Line Chart with daily trends
#-------------------
st.plotly_chart(fig, use_container_width=True)
#-------------------


#------------------------------------------
# Table with a color-coded column
df_scrape["color"] = df_scrape["% Change"].map(lambda x:'red' if x<0 else 'green')
cols_to_show = ['Symbol','Name', 'Price', '% Change', 'Market Cap']
# to change color of "% change" column
fill_color = []
n = len(df_scrape)
for col in cols_to_show:
    if col!='% Change':
        fill_color.append(['black']*n)
    else:
        fill_color.append(df_scrape["color"].to_list())
# Plotly Table
data=[go.Table(columnwidth = [20,15,15,15,15],
                header=dict(values=[f"<b>{col}</b>" for col in cols_to_show],
                font=dict(color='white', size=20),
                height=30,
                line_color='black',
                fill_color='dimgrey',
                align=['left','left', 'right','right','right']),
                cells=dict(values=df_scrape[cols_to_show].values.T,
               fill_color=fill_color,
               font=dict(color='white', size=20),
               height=30,
               line_color='black',
               align=['left','left', 'right','right','right']))]
fig = go.Figure(data=data)
fig.update_layout(go.Layout(xaxis = {'showgrid': False},
                  yaxis = {'showgrid': False}))

#-------------------
# Table showing top 25 cryptos
#-------------------
st.plotly_chart(fig, use_container_width=True)
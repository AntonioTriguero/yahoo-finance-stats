from datetime import datetime
import pandas as pd
from itertools import product
import numpy as np
import streamlit as st
from yfinance import Ticker
from stockstats import StockDataFrame
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer

class Stock(Ticker):
    def __init__(self, ticker, session=None):
        super().__init__(ticker, session=session)
        self.__intervals = {'1 day': '1d', '5 days': '5d', '1 week': '1wk', '1 month': '1mo', '3 months': '3mo'}
        self.__indicators = {'KDJ': 'kdjk', 'Bolling': 'boll', 'Bolling Upper Band': 'boll_ub', 
                            'Bolling Lower Band': 'boll_lb', 'DMA': 'dma', 'TRIX': 'trix',
                            'CCI': 'cci', '6 days RSI': 'rsi_6', '12 days RSI': 'rsi_12',
                            '10 days WR': 'wr_10', '6 days WR': 'wr_6', '20 days CCI': 'cci_20'}

    @st.cache
    def history(self, period="1mo", interval="1 day", start=None, end=None, prepost=False, actions=True, auto_adjust=True, back_adjust=False, proxy=None, rounding=False, tz=None, **kwargs):
        return super().history(period=period, interval=self.__intervals[interval], start=start, end=end, prepost=prepost, actions=actions, auto_adjust=auto_adjust, back_adjust=back_adjust, proxy=proxy, rounding=rounding, tz=tz, **kwargs)

    @st.cache
    def indicators(self, period="1mo", interval="1 day", start=None, end=None, prepost=False, actions=True, auto_adjust=True, back_adjust=False, proxy=None, rounding=False, tz=None, **kwargs):
        hist = self.history(period=period, interval=interval, start=start, end=end, prepost=prepost, actions=actions, auto_adjust=auto_adjust, back_adjust=back_adjust, proxy=proxy, rounding=rounding, tz=tz, **kwargs)
        stockdf = StockDataFrame.retype(hist)
        result = pd.DataFrame(index=stockdf.index, columns=self.__indicators.keys())
        result[list(self.__indicators.keys())] = stockdf[list(self.__indicators.values())]
        return result

    @st.cache
    def change(self, period="1mo", interval="1 day", start=None, end=None, prepost=False, actions=True, auto_adjust=True, back_adjust=False, proxy=None, rounding=False, tz=None, **kwargs):
        hist = self.history(period=period, interval=interval, start=start, end=end, prepost=prepost, actions=actions, auto_adjust=auto_adjust, back_adjust=back_adjust, proxy=proxy, rounding=rounding, tz=tz, **kwargs)
        stockdf = StockDataFrame.retype(hist)
        result = pd.DataFrame(index=stockdf.index, columns=['Change'])
        result['Change'] = stockdf['change']
        return result

    @st.cache
    def news(self) -> pd.DataFrame:
        url = f'https://finviz.com/quote.ashx?t={self.ticker}'
        req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
        html = BeautifulSoup(urlopen(req), features="lxml")
        news_table = html.find(id='news-table')

        vader, index, rows = SentimentIntensityAnalyzer(), [], []
        for x in news_table.findAll('tr'):
            date_scrape = x.td.text.split()
            if len(date_scrape) == 2:
                headline = x.a.get_text()
                sentiment = vader.polarity_scores(headline)

                index.append(datetime.strptime(f'{date_scrape[0]}', '%b-%d-%y').strftime('%b-%d-%y'))
                rows.append([headline, *sentiment.values()])

        return pd.DataFrame(rows,
                            columns=['Headline', 'Negative', 'Neutral', 'Positive', 'Compound'],
                            index=index)

    @st.cache
    def financials_slopes(self) -> pd.DataFrame:
        result = self.quarterly_financials.transpose()
        result.index = result.index.year
        index = np.array(list(product(result.index[[0, -1]], result.columns)))
        result = pd.DataFrame(
            [index[:, 0], index[:, 1], result.values[[0, -1]].flatten()]
        ).transpose().dropna()
        result.columns = ['Date', 'Stat', 'Value']
        return result

    @st.cache
    def financials(self) -> pd.DataFrame:
        source = self.quarterly_financials.dropna()
        source = source.transpose()
        source.index = source.index.round('d')
        return source

    @st.cache
    def actions_recommendations(self, period="1mo", interval="1 day", start=None, end=None, columns=[]) -> pd.DataFrame:
        recom = self.recommendations.copy()
        recom.index = recom.index.round('d')
        recom = recom[recom['To Grade'].isin(columns)]
        recom = recom.rename(columns={'To Grade': 'Recommendation'})

        history = self.history(period=period, interval=interval, start=start, end=end)
        source = pd.merge_ordered(history.reset_index(), recom.reset_index(), left_by="Date")
        return source.fillna('')


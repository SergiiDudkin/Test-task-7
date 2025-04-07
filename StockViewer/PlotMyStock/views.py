from django.shortcuts import render
import yfinance as yf
import plotly.graph_objects as go
from plotly.io import to_html

# Create your views here.

SYMBOLS_ALL = sorted(["GBXXY", "RASP", "GOOGL", "MSFT", "BAC", "DTMXF", "EESE", "DGLY", "AKOM"])

TABLE_FIELDS = [
    ("marketCap", "Market capitalization, a key indicator of a company's size"),
    ("currentPrice", "The latest trading price of the stock"),
    ("previousClose", "The closing price from the previous trading session"),
    ("open", "The price at which the stock opened for trading"),
    ("volume", "Number of shares traded during the day"),
    ("epsTrailingTwelveMonths", "Earnings per share over the past 12 months"),
    ("trailingPE", "Price-to-earnings ratio based on the trailing 12 months"),
    ("forwardPE", "Price-to-earnings ratio based on projected future earnings"),
    ("bookValue", "The net asset value of the company"),
    ("priceToBook", "Market price compared to book value per share"),
    ("dividendYield", "Annual dividend income as a percentage of the stock price"),
    ("dividendRate", "Total expected annual dividend payout per share"),
    ("beta", "A measure of the stock’s volatility relative to the market"),
    ("revenuePerShare", "Revenue allocated per share"),
    ("netIncomeToCommon", "Net income attributable to common shareholders"),
    ("averageAnalystRating", "Consensus recommendation from financial analysts")
]


def index(request):
    data = {'title': 'Home', 'symbols_all': SYMBOLS_ALL}
    return render(request, 'index.html', data)


def show_ticker(request, symbol):
    ticker_obj = yf.Ticker(symbol)
    ticker_info = ticker_obj.info

    hist_df = ticker_obj.history(period="1y", interval="1wk").reset_index()
    candlestick = go.Candlestick(x=hist_df['Date'],
                                 open=hist_df['Open'],
                                 high=hist_df['High'],
                                 low=hist_df['Low'],
                                 close=hist_df['Close'],
                                 increasing_line_color = 'seagreen',
                                 decreasing_line_color = 'crimson')
    fig = go.Figure(data=[candlestick])
    fig.update_layout(margin={"t": 0, "l": 0, "r": 3, "b": 0},
                      plot_bgcolor='rgba(0.97, 0.97, 0.97, 1)',
                      paper_bgcolor='rgba(0, 0, 0, 0)')
    fig.update_xaxes(mirror=True, showline=True, linecolor='lightgrey', gridcolor='lightgrey')
    fig.update_yaxes(mirror=True, showline=True, linecolor='lightgrey', gridcolor='lightgrey')
    html_chart = to_html(fig,
                         full_html=False,
                         config={'displaylogo': False,
                                 'modeBarButtonsToRemove': ['select2d', 'lasso2d']})

    fin_metrics = [(param, descr, ticker_info.get(param, '&#8212;')) for param, descr in TABLE_FIELDS]

    data = {'candlestick_chart': html_chart,
            'company_name': ticker_info['longName'],
            'fin_metrics': fin_metrics,
            'symbols_all': SYMBOLS_ALL}

    return render(request, 'chart.html', data)

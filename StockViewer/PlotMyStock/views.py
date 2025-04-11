import numbers
from datetime import datetime
from typing import Any

import plotly.graph_objects as go
import yfinance as yf
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from plotly.io import to_html


# Settings

SYMBOLS_ALL = sorted(["BMW.DE", "BABA", "GBXXY", "RASP", "GOOGL", "MSFT", "BAC", "DTMXF", "EESE", "DGLY", "AKOM"])
PERIODS_ALL = ["6mo", "1y", "5y", "10y", "ytd", "max"]
INTERVALS_ALL = ["1d", "1wk", "1mo", "3mo"]

TABLE_FIELDS = [
    ("Previous Close", "The closing price from the previous trading session",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "previousClose")),
    ("Open", "The first executed trade from the latest trading session",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "open")),
    ("Bid", "An offer made by an individual or entity to purchase an asset",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "bid")),
    ("Ask", "An offer price",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "ask")),
    ("Day's Range", "Difference between the highest and lowest prices during a single trading day",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "regularMarketDayRange")),
    ("52 Week Range", "Difference between the highest and lowest prices during a single trading day the past 52 weeks",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "fiftyTwoWeekRange")),
    ("Volume", "The total number of shares traded for a specific security during a regular trading session",
     lambda ticker_obj: get_val(ticker_obj, "regularMarketVolume")),
    ("Avg. Volume", "90 Days daily average volume",
     lambda ticker_obj: get_val(ticker_obj, "averageVolume")),
    ("Market Cap", "The total market value of a company's outstanding shares",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "marketCap")),
    ("Beta (5Y Monthly)", "A measure of a stock's volatility in relation to the overall market",
     lambda ticker_obj: get_val(ticker_obj, "beta")),
    ("PE Ratio (TTM)", "Price-to-earnings ratio based on the trailing 12 months",
     lambda ticker_obj: get_val(ticker_obj, "trailingPE")),
    ("EPS (TTM)", "Earnings per share calculated over the trailing twelve months",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "trailingEps")),
    ("Earnings Date", "The period when a company publicly announces its earnings",
     lambda ticker_obj: get_earnings_date(ticker_obj)),
    ("Dividend Rate", "Annual dividend payment per share",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "dividendRate")),
    ("Forward Dividend Yield", "An estimate of next year's dividend given as a percentage of the current stock price",
     lambda ticker_obj: get_val(ticker_obj, "dividendYield") + "%"),
    ("Ex-Dividend Date", "The date by which an investor must own a stock in order to receive the next dividend payment",
     lambda ticker_obj: get_exdividend_date(ticker_obj)),
    ("1y Target Est", "Median target price forecasted by analysts over the next year",
     lambda ticker_obj: get_val_with_currency(ticker_obj, "targetMedianPrice")),
]

CURRENCY_DICT = {
    "USD": "&#36;",
    "EUR": "&#8364;",
    "CNY": "&#20803;",
}


# Views

def index(request: WSGIRequest) -> HttpResponse:
    data = {"title": "Home",
            "symbols_all": SYMBOLS_ALL,
            "curr": {"symbol": "", "period": "6mo", "interval": "1d"}}
    return render(request, "index.html", data)


def show_ticker(request: WSGIRequest, symbol: str, period: str, interval: str) -> HttpResponse:
    ticker_obj = yf.Ticker(symbol)
    data = {"title": symbol,
            "candlestick_chart": make_html_candle_chart(ticker_obj, period, interval),
            "fin_metrics": make_metrics_table(ticker_obj),
            "company_name": ticker_obj.info["longName"],
            "symbols_all": SYMBOLS_ALL,
            "periods": PERIODS_ALL,
            "intervals": INTERVALS_ALL,
            "curr": {"symbol": symbol, "period": period, "interval": interval}}

    return render(request, "chart.html", data)


# Helpers

def make_metrics_table(ticker_obj: yf.Ticker) -> list[list[tuple[str, str, Any]]]:
    """
    Extracts and formats data for output.

    Args:
        ticker_obj: The source of data.

    Returns:
        Key financial metrics in the form of three tables
    """
    table = [(metric_name, description, value_func(ticker_obj))
             for metric_name, description, value_func in TABLE_FIELDS]

    # Split one table into three (FIX for Mozilla Firefox)
    max_row_num = (len(table) + 2) // 3
    tables = [table[i * max_row_num: (i + 1) * max_row_num] for i in range(3)]

    return tables


def get_val(ticker_obj: yf.Ticker, field: str):
    val = ticker_obj.info.get(field, "&#8212;")
    return f"{val:,}" if isinstance(val, numbers.Number) else val


def get_val_with_currency(ticker_obj: yf.Ticker, field: str) -> str:
    currency = ticker_obj.info["currency"]
    return f"{CURRENCY_DICT.get(currency, currency)} {get_val(ticker_obj, field)}"


def get_exdividend_date(ticker_obj: yf.Ticker) -> str:
    timestamp = ticker_obj.info.get("exDividendDate")
    return datetime.utcfromtimestamp(timestamp).strftime("%b %d, %Y") if timestamp else "&#8212;"


def get_earnings_date(ticker_obj: yf.Ticker) -> str:
    date_st = ticker_obj.info['earningsTimestampStart']
    date_en = ticker_obj.info['earningsTimestampEnd']
    earnings_date = datetime.utcfromtimestamp(date_st).strftime("%b %d, %Y")
    if date_st != date_en:
        earnings_date += " - " + datetime.utcfromtimestamp(date_en).strftime('%b %d, %Y')
    return earnings_date


def make_html_candle_chart(ticker_obj: yf.Ticker, period: str, interval: str) -> str:
    """
    Creates candlestick chart of historical stock prices.

    Args:
        ticker_obj: The source of data.

    Returns:
        HTML element as a string.
    """
    hist_df = ticker_obj.history(period=period, interval=interval).reset_index()
    candlestick = go.Candlestick(x=hist_df["Date"],
                                 open=hist_df["Open"],
                                 high=hist_df["High"],
                                 low=hist_df["Low"],
                                 close=hist_df["Close"],
                                 increasing_line_color="seagreen",
                                 decreasing_line_color="crimson")
    fig = go.Figure(data=[candlestick])
    fig.update_layout(margin={"t": 0, "l": 0, "r": 3, "b": 0},
                      plot_bgcolor="rgba(0.97, 0.97, 0.97, 1)",
                      paper_bgcolor="rgba(0, 0, 0, 0)",
                      yaxis_title=f"Stock price, {ticker_obj.info['currency']}")
    fig.update_xaxes(mirror=True, showline=True, linecolor="lightgrey", gridcolor="lightgrey")
    fig.update_yaxes(mirror=True, showline=True, linecolor="lightgrey", gridcolor="lightgrey")
    html_chart = to_html(fig,
                         full_html=False,
                         config={"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]})
    return html_chart

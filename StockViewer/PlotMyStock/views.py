import plotly.graph_objects as go
import yfinance as yf
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from plotly.io import to_html


# Settings

SYMBOLS_ALL = sorted(["GBXXY", "RASP", "GOOGL", "MSFT", "BAC", "DTMXF", "EESE", "DGLY", "AKOM"])

TABLE_FIELDS = [
    ("bid", "An offer made by an individual or entity to purchase an asset."),
    ("ask", "An offer price."),
    ("regularMarketDayRange", "Difference between the highest and lowest prices during a single trading day"),
    ("fiftyTwoWeekRange", "Difference between the highest and lowest prices during a single trading day the past 52 "
                          "weeks"),
    ("regularMarketVolume", "The total number of shares or contracts traded for a specific security during a regular "
                            "trading session"),
    ("averageVolume", "90 Days daily average volume"),
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


# Views

def index(request: WSGIRequest) -> HttpResponse:
    data = {"title": "Home", "symbols_all": SYMBOLS_ALL}
    return render(request, "index.html", data)


def show_ticker(request: WSGIRequest, symbol: str) -> HttpResponse:
    ticker_obj = yf.Ticker(symbol)

    fin_metrics = [(param, descr, ticker_obj.info.get(param, "&#8212;")) for param, descr in TABLE_FIELDS]

    data = {"candlestick_chart": make_html_candle_chart(ticker_obj),
            "fin_metrics": fin_metrics,
            "company_name": ticker_obj.info["longName"],
            "symbols_all": SYMBOLS_ALL,
            "symbol": symbol}

    return render(request, "chart.html", data)


# Helpers

def make_html_candle_chart(ticker_obj: yf.Ticker) -> str:
    """
    Creates candlestick chart of historical stock prices.

    Args:
        ticker_obj: The source of data.

    Returns:
        HTML element as a string.
    """
    hist_df = ticker_obj.history(period="1y", interval="1wk").reset_index()
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

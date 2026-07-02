import yfinance as yf


def fetch_close_prices(ticker: str, period: str = "1mo"):
    data = yf.Ticker(ticker).history(period=period)
    return data["Close"]

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go


st.set_page_config(
    page_title="Crypto AI Analyzer",
    layout="wide"
)

st.title("🤖 Crypto AI Analyzer")
st.caption("تحلیل بازار - نسخه آزمایشی")


coins = {
    "Bitcoin": "BTC",
    "Ethereum": "ETH",
    "Solana": "SOL"
}


coin_name = st.selectbox(
    "انتخاب ارز",
    list(coins.keys())
)

symbol = coins[coin_name]


def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1h&limit=200"
        data = requests.get(url, timeout=10).json()

        df = pd.DataFrame(data)

        df = df.iloc[:, :6]
        df.columns = [
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        for c in df.columns[1:]:
            df[c] = df[c].astype(float)

        return df

    except Exception:
        return None



df = get_price(symbol)


if df is None:
    st.error("دریافت اطلاعات بازار انجام نشد")
    st.stop()


# RSI
delta = df["close"].diff()

gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss

df["RSI"] = 100 - (100 / (1 + rs))


# Moving Average

df["MA20"] = df["close"].rolling(20).mean()
df["MA50"] = df["close"].rolling(50).mean()


last_price = df["close"].iloc[-1]
rsi = df["RSI"].iloc[-1]


if rsi < 30:
    signal = "🟢 احتمال اشباع فروش"
elif rsi > 70:
    signal = "🔴 احتمال اشباع خرید"
else:
    signal = "🟡 خنثی"



risk = 0.02

stop_loss = last_price * (1-risk)

take_profit = last_price * (1+(risk*2))


col1, col2, col3 = st.columns(3)


col1.metric(
    "قیمت فعلی",
    f"{last_price:.2f} USDT"
)

col2.metric(
    "RSI",
    f"{rsi:.2f}"
)

col3.metric(
    "وضعیت",
    signal
)



st.subheader("نمودار")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["close"],
        name="Price"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MA20"],
        name="MA20"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["MA50"],
        name="MA50"
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


st.subheader("مدیریت ریسک")

st.write(
    f"""
    قیمت ورود پیشنهادی: {last_price:.2f}

    حد ضرر پیشنهادی: {stop_loss:.2f}

    حد سود پیشنهادی: {take_profit:.2f}
    """
)


st.info(
    "این ابزار تحلیل است و تضمین سود یا سیگنال قطعی معامله نیست."
)

import streamlit as st
import pandas as pd
import pandas_ta as ta
import requests

st.set_page_config(page_title="Crypto AI Trader", layout="centered")

st.title("🚀 Crypto AI Trader Pro")
st.subheader("تحلیل لحظه‌ای بازار با هوش مصنوعی")

# انتخاب ارز
symbol = st.selectbox("ارز مورد نظر را انتخاب کنید:", ["BTCUSDT", "ETHUSDT", "SOLUSDT"])

class CryptoAnalyzer:
    def __init__(self, symbol="BTCUSDT", interval="1h"):
        self.symbol = symbol
        self.interval = interval
        self.base_url = "https://api.binance.com/api/v3/klines"

    def fetch_data(self):
        try:
            params = {'symbol': self.symbol, 'interval': self.interval, 'limit': 100}
            res = requests.get(self.base_url, params=params, timeout=5)
            data = res.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric)
            return df
        except Exception as e:
            return None

    def analyze(self):
        df = self.fetch_data()
        if df is None or len(df) < 30:
            return None
        
        df['RSI'] = ta.rsi(df['close'], length=14)
        macd = ta.macd(df['close'])
        df = pd.concat([df, macd], axis=1)
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        last_row = df.iloc[-1]
        current_price = last_row['close']
        rsi = last_row['RSI']
        macd_line = last_row.get('MACD_12_26_9', 0)
        macd_signal = last_row.get('MACDs_12_26_9', 0)
        atr = last_row.get('ATR', current_price * 0.01)

        signal = "WAIT"
        stop_loss = 0
        take_profit = 0

        if rsi < 45 and macd_line > macd_signal:
            signal = "BUY"
            stop_loss = current_price - (atr * 2)
            take_profit = current_price + (atr * 3)
        elif rsi > 55 and macd_line < macd_signal:
            signal = "SELL"
            stop_loss = current_price + (atr * 2)
            take_profit = current_price - (atr * 3)

        return {
            "symbol": self.symbol,
            "price": round(current_price, 2),
            "signal": signal,
            "rsi": round(rsi, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2)
        }

if st.button("شروع تحلیل زنده بازار"):
    with st.spinner('در حال اتصال به صرافی و محاسبه اندیکاتورها...'):
        analyzer = CryptoAnalyzer(symbol=symbol)
        result = analyzer.analyze()
        
        if result:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("قیمت لحظه‌ای", f"${result['price']}")
                st.metric("RSI", result['rsi'])
            
            with col2:
                sig = result['signal']
                color = "green" if sig == "BUY" else "red" if sig == "SELL" else "orange"
                st.markdown(f"### سیگنال: :{color}[{sig}]")

            if sig != "WAIT":
                st.success(f"""
                **نقاط پیشنهاد معامله:**
                - حد ضرر (Stop Loss): **{result['stop_loss']}**
                - حد سود (Take Profit): **{result['take_profit']}**
                """)
            else:
                st.warning("بازار در حالت رنج (Neutral) است. بهتر است صبر کنید.")
        else:
            st.error("خطا در دریافت اطلاعات از صرافی. لطفاً دوباره تلاش کنید.")

st.sidebar.markdown("---")
st.sidebar.write("📌 **راهنمای نصب روی گوشی:**")
st.sidebar.write("در مرورگر کروم گوشی، منوی بالا (سه نقطه) را بزنید و گزینه **Add to Home Screen** را انتخاب کنید تا مثل یک اپلیکیشن روی گوشی شما نصب شود.")


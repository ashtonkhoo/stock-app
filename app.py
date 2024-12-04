import os
import json
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from openai import AzureOpenAI
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv('credentials_gpt4.env')

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

st.set_page_config(page_title="LLM Stock Prediction")

# Title and instructions
st.title("LLM-Powered Stock and Crypto Predictor")

# Sidebar for ticker selection
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="BTC-USD")
interval = st.sidebar.text_input("Enter Interval", value="5m")
st.sidebar.markdown("[Click here for full list of tickers](https://finance.yahoo.com/lookup/)")
days_to_fetch = st.sidebar.slider("Days of data to fetch", min_value=1, max_value=59, value=3)

# Fetch data
def fetch_data(ticker, days, interval):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval, ignore_tz=False)
        data.index = data.index.tz_convert('Asia/Kuala_Lumpur')
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_data(ticker, days_to_fetch, interval)
data = data.round(4)

if data is not None and not data.empty:
    # Display chart
    day_str = "Day" if days_to_fetch == 1 else "Days"
    st.subheader(f"{yf.Ticker(ticker).info['shortName']} Price Chart (Last {days_to_fetch} {day_str})")
    
    plot_df = pd.DataFrame(data.reset_index().to_numpy(), columns=['Datetime', *[c[0] for c in data.columns]])
    
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=plot_df['Datetime'],
                open=plot_df['Open'],
                high=plot_df['High'],
                low=plot_df['Low'],
                close=plot_df['Close']
            )
        ]
    )
    fig.update_layout(xaxis_rangeslider_visible=False)      
    
    high = max(plot_df["High"])
    low = min(plot_df["Low"])
    
    # Calculate Fibonacci levels
    fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    fib_values = [low + (high - low) * level for level in fib_levels]

    # Define color mapping for Fibonacci levels
    fib_colors = {
        0: "green",         # 0% - Support
        0.236: "lightblue", # 23.6%
        0.382: "orange",    # 38.2%
        0.5: "gray",        # 50%
        0.618: "gold",      # 61.8%
        0.786: "purple",    # 78.6%
        1: "red"            # 100% - Resistance
    }

    # Add Fibonacci levels to the chart
    for level, value in zip(fib_levels, fib_values):
        # Get color from the mapping, default to gray if not found
        color = fib_colors.get(level, "gray")
        text = "Support" if level == 0 else "Resistance" if level == 1 else f"{level*100:.1f}%"
        
        # Add horizontal line with annotation
        fig.add_hline(
            y=value,
            line=dict(
                color=color,
                dash="dash" if level not in [0, 1] else "solid",
                width=2
            ),
            annotation_text=text,
            annotation_position="top left"
        )
        
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )
    
    st.plotly_chart(fig)

    # Prepare data summary for LLM
    st.subheader("LLM Prediction")
    last_close = data['Close'].iloc[-1]
    summary = data.describe()
    vol_change = summary.get('Close').T.get('std').values.tolist()[0]
    avg_volume = summary.get('Volume').T.get('mean').values.tolist()[0]

    prompt = f"""
        You are a financial analyst with solid expertise in technical and fundamental analysis. 
        Based on the data below, provide a recommendation to either 'Buy', 'Sell', or 'Hold' the asset. 
        Your response should include a decision, reasoning, and any key risks. Here is the data:

        - Ticker: {ticker}
        - Last Close Price: {str(last_close)}
        - Price Volatility (Std Dev): {str(vol_change)}
        - Average Volume: {str(avg_volume)}
        - Recent Closing Prices: {data['Close'].tail(5).to_numpy().flatten().tolist()}
        - Support Line: {str(fib_values[0])}
        - Resistance Line: {str(fib_values[-1])}

        Consider both short-term (next week) and long-term (next quarter) factors.
        Provide your response in the following format:
        - Decision: 'Buy', 'Sell', or 'Hold'
        - Reasoning: A concise explanation based on the data above.
        - Key Risks: Any potential risks or uncertainties impacting your recommendation.
        
        Use comma notation for large numbers, and include the currency before the values.
        Use plaintext when you want to show mathematical expressions.
    """


    # Call Azure OpenAI model for prediction
    try:
        with st.spinner("Analyzing market data..."):
            chat_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
            )
        llm_output = json.loads(chat_completion.model_dump_json())['choices'][0]['message']['content'].replace("$", "\\$")
        st.markdown(f"{llm_output}", unsafe_allow_html=False)
    except Exception as e:
        st.error(f"Error interacting with Azure OpenAI: {e}")

else:
    st.warning("No data found. Please check the ticker symbol and date period, and try again.")

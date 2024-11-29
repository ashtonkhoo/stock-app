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
def fetch_data(ticker, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval, ignore_tz=False)
        data.index = data.index.tz_convert('Asia/Kuala_Lumpur')
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

data = fetch_data(ticker, days_to_fetch)
data = data.round(4)

if data is not None and not data.empty:
    # Display chart
    st.subheader(f"{yf.Ticker(ticker).info['shortName']} Price Chart (Last {days_to_fetch} Days)")
    
    plot_df = pd.DataFrame(data.reset_index().to_numpy(), columns=['Datetime', *[c[0] for c in data.columns]])

    support = []
    resistance = []

    for i in range(1, len(plot_df) - 1):  # Ignore the first and last elements
        if plot_df.iloc[i]['Close'] < plot_df.iloc[i - 1]['Close'] and plot_df.iloc[i]['Close'] < plot_df.iloc[i + 1]['Close']:
            support.append(plot_df.iloc[i]['Close'])
        elif plot_df.iloc[i]['Close'] > plot_df.iloc[i - 1]['Close'] and plot_df.iloc[i]['Close'] > plot_df.iloc[i + 1]['Close']:
            resistance.append(plot_df.iloc[i]['Close'])

    # Calculate constant support and resistance levels
    constant_support = min(support) if support else None
    constant_resistance = max(resistance) if resistance else None    
    
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
    
    fig.add_hline(y=constant_support, line=dict(color='green', dash='dash', width=2), 
                  annotation_text="Support", annotation_position="top right")
    fig.add_hline(y=constant_resistance, line=dict(color='red', dash='dash', width=2), 
                  annotation_text="Resistance", annotation_position="top right")
    
    st.plotly_chart(fig)

    # Prepare data summary for LLM
    st.subheader("Prediction Section")
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
        - Support Line: {str(constant_support)}
        - Resistance Line: {str(constant_resistance)}

        Consider both short-term (next week) and long-term (next quarter) factors.
        Provide your response in the following format:
        - Decision: 'Buy', 'Sell', or 'Hold'
        - Reasoning: A concise explanation based on the data above.
        - Key Risks: Any potential risks or uncertainties impacting your recommendation.
        
        Do not use markdown notation anywhere in the response.
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
        llm_output = json.loads(chat_completion.model_dump_json())['choices'][0]['message']['content']
        st.markdown(f"**LLM Prediction:**\n {llm_output}", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error interacting with Azure OpenAI: {e}")

else:
    st.warning("No data found. Please check the ticker symbol and date period, and try again.")

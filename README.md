
# LLM-Powered Stock and Crypto Predictor

This application utilizes **Azure OpenAI** & **Yahoo Finance (yfinance)** to provide stock and cryptocurrency predictions. The app fetches live market data, performs technical analysis (support and resistance levels), and leverages the **GPT-4o** model for recommendation insights.

---

## Features

1. **Live Market Data**  
   Fetch real-time stock or cryptocurrency data using Yahoo Finance.  
   - User-defined ticker symbols.  
   - Customizable interval and date range.

2. **Technical Charting**  
   Visualize data using an interactive candlestick chart with:  
   - Constant **Support** and **Resistance** levels.

3. **LLM-Powered Insights**  
   Leverage **GPT-4o** to get:  
   - Predictions: Buy, Sell, or Hold.  
   - Concise reasoning and risk assessments.  

4. **User-Friendly Interface**  
   Accessible via an intuitive sidebar for input configuration.

---

## Installation

Follow these steps to set up the project on your local machine:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ashtonkhoo/stock-app.git
   cd stock-app
   ```

2. **Set Up Python Environment**
   Install Python (>= 3.8) and create a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate    # On macOS/Linux
   venv\Scripts\activate       # On Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**  
   Create a file named `credentials_gpt4.env` in the project directory. Add the following variables:  
   ```env
   AZURE_OPENAI_API_KEY=<your_api_key>
   AZURE_OPENAI_API_VERSION=<api_version>
   AZURE_OPENAI_ENDPOINT=<api_endpoint>
   ```

5. **Run the Application**
   Start the Streamlit app with:  
   ```bash
   streamlit run app.py
   ```

---

## Usage

1. **Enter Ticker Symbol**  
   Input a stock or cryptocurrency ticker symbol (e.g., `BTC-USD` for Bitcoin).  

2. **Set Date Interval and Range**  
   Customize the interval (e.g., `5m`, `1d`) and fetch up to 59 days of data.  

3. **View Charts**  
   - Explore the candlestick chart with calculated **Support** and **Resistance** levels.  

4. **Get Predictions**  
   - Receive Buy/Sell/Hold recommendations with reasoning and risk assessments directly from GPT-4.

---

## Dependencies

- **Python Libraries**:  
  - `streamlit`  
  - `yfinance`  
  - `plotly`  
  - `pandas`  
  - `dotenv`  
  - `openai`  

- **APIs**:  
  - **Azure OpenAI** for LLM insights.  
  - **Yahoo Finance** for market data.

---

## Known Issues

- The app supports a maximum data fetch range of **59 days** due to Yahoo Finance limitations.  
- Ensure valid ticker symbols to prevent data retrieval errors.  

---

## License

This project is licensed under the **MIT License**.

---

For questions or issues, feel free to raise an issue or reach out via the repository! 🚀

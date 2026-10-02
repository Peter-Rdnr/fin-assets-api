from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from datetime import datetime, timedelta

app = FastAPI(title="Fin Assets API")

# CORS configuration for web client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chart")
def get_chart_data(
    symbol: str = Query(..., description="The ticker symbol, e.g. AAPL"),
    years: int = Query(2, description="Number of years to look back")
):
    try:
        # Calculate the time period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        # Retrieve data from YF
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval="1d"
        )
        
        if df.empty:
            return {"error": f"No data found for symbol '{symbol}'."}
        
        # Format the data for the API response
        df = df.reset_index()
        chart_data = []
        
        for _, row in df.iterrows():
            chart_data.append({
                "date": row['Date'].strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
            
        return {
            "symbol": symbol.upper(),
            "years": years,
            "data": chart_data
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"status": "API is running."}

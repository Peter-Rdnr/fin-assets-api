from fastapi import FastAPI, Query, Response, status
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
    years: int = Query(2, description="Number of years to look back"),
    fields: str = Query("C", description="String containing letters O, H, L, C, V to filter data")
):
    try:
        # Calculate the time period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        # Define fields
        field_mask = fields.upper()
        columns = ["date"]
        if "O" in field_mask: columns.append("open")
        if "H" in field_mask: columns.append("high")
        if "L" in field_mask: columns.append("low")
        if "C" in field_mask: columns.append("close")
        if "V" in field_mask: columns.append("volume")
        
        # Retrieve data from YF
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval="1d"
        )
        
        if df.empty:
            return []
        
        # Format the data for the API response
        df = df.reset_index()
        chart_data = []
        
        for _, row in df.iterrows():
            row_data = [row['Date'].tz_localize(None).strftime('%Y-%m-%d')]
            if "O" in field_mask: row_data.append(round(row['Open'], 2))
            if "H" in field_mask: row_data.append(round(row['High'], 2))
            if "L" in field_mask: row_data.append(round(row['Low'], 2))
            if "C" in field_mask: row_data.append(round(row['Close'], 2))
            if "V" in field_mask: row_data.append(int(row['Volume']))
            chart_data.append(row_data)
            
        return chart_data
        
    except Exception as e:
        return []

@app.get("/")
def read_root():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

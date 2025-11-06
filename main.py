import uvicorn
from weather_api import app

if __name__ == "__main__":
    print("Weather API with Chat History: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
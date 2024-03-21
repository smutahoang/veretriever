import uvicorn
from api import app

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=5001, log_level="info")

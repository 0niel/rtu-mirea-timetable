import uvicorn
from app import config

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        reload=config.RELOAD,
    )

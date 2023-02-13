import uvicorn
from app.config import config

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        debug=config.DEBUG,
        reload=config.BACKEND_RELOAD,
    )

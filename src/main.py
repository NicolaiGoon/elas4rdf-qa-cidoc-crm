import uvicorn

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 5000
    app_name = "src.app:app"
    uvicorn.run(app=app_name, host="0.0.0.0", port=port, reload=True)

def main() -> None:
    import os
    import uvicorn

    uvicorn.run("grub_map_api.app:app", host=os.environ.get("HOST", "127.0.0.1"),
                port=int(os.environ.get("PORT", "8000")), reload=os.environ.get("RELOAD") == "1")

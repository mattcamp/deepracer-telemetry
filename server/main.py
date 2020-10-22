from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel

from asyncio import Queue

queue: Queue = None


app = FastAPI()
app.mount("/html", StaticFiles(directory="html"), name="html")

@app.get("/")
async def read_index():
    return RedirectResponse(url="/html/index.html")


@app.get("/test")
async def read_test():
    return RedirectResponse(url="/html/test.html")


@app.put("/throttle")
async def update_throttle(throttle: int = Body(...)):
    results = {"throttle": throttle}
    print("got throttle %s" % str(throttle))
    return results


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global queue
    queue = Queue()
    while True:
        msg = await queue.get()
        await websocket.send_text(msg)



@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    global queue
    try:
        while True:
            data = await websocket.receive_text()
            if queue:
                await queue.put(data)
            else:
                print("no queue")

    except WebSocketDisconnect:
        print("Websocket disconnected")

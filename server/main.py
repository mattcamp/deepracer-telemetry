from fastapi import FastAPI, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from fastapi_utils.tasks import repeat_every

from asyncio import Queue

queue: Queue = None

app = FastAPI()
app.mount("/html", StaticFiles(directory="html"), name="html")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_to_self(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        # print("Broadcasting %s" % message)
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.on_event("startup")
@repeat_every(seconds=1)
async def ping():
    await manager.broadcast(message="ping")


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
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print("Received data: %s" % data)
    except WebSocketDisconnect:
        print(f"Viewer websocket disconnected")
        manager.disconnect(websocket)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} websocket disconnected")
        manager.disconnect(websocket)


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     global queue
#     queue = Queue()
#     while True:
#         msg = await queue.get()
#         await websocket.send_text(msg)
#
#
#
#
# @app.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     await websocket.accept()
#     global queue
#     try:
#         while True:
#             data = await websocket.receive_text()
#             if queue:
#                 await queue.put(data)
#             else:
#                 print("no queue")
#
#     except WebSocketDisconnect:
#         print("Websocket disconnected")
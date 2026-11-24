import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])

@sio.event
async def connect(sid, environ, auth=None):
    # Authenticate the Socket.IO connection with a JWT before enabling private chat
    # events in production. REST chat endpoints are available meanwhile.
    return True

@sio.event
async def disconnect(sid):
    pass

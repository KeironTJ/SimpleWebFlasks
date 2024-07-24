from app import socketio

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('my event')
def handle_my_custom_event(data):
    print('received data: ' + str(data))
    socketio.emit('my response', {'data': 'This is a response from the server!'})
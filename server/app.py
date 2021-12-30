import logging
from logging import debug
from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect 
from colorama import init, Fore, Back
init(autoreset=True)

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins="*")
thread = None
thread_lock = Lock()
playerBuffer_num = dict()
playerBuffer_sid = dict()
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1

@socketio.event
def tank_down(message):
    print(message)
    session['receive_count'] = session.get('receive_count', 0) + 1
    try:
        emit('move_down',
            {'down': message['data'], "mysid":request.sid,"room":message['room']},to=message['room'])
        print({'down': message['data'], "mysid":request.sid,"room":message['room']})
    except Exception as e:
        print(e)
        emit('my_response',
         {'data': "Please join room!!",
          'count': session['receive_count']})

@socketio.event
def tank_up(message):
    print(message)
    session['receive_count'] = session.get('receive_count', 0) + 1
    try:
        emit('move_up',
            {'up': message['data'], "mysid":request.sid,"room":message['room']}, to=message['room'])
        print({'up': message['data'], "mysid":request.sid,"room":message['room']})
    except Exception as e:
        print(e)
        emit('my_response',
         {'data': "Please join room!!",
          'count': session['receive_count']})
@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.event
def join(message):
    global playerBuffer_num
    global playerBuffer_sid
    print(message, request.sid)
    if (playerBuffer_num.get(message['room']) and message['clientSid'] != playerBuffer_sid[message['room']][0]):
        playerBuffer_num[message['room']] += 1
        if(playerBuffer_num[message['room']]==2):
            playerBuffer_sid[message['room']].append(request.sid)
            join_room(message['room'])
            session['receive_count'] = session.get('receive_count', 0) + 1
            emit('my_response',
                {'data': 'In rooms: ' + ', '.join(rooms()),
                'count': session['receive_count']},to=message['room'])
            emit('my_response', {'data': 'Two Player Enter.', 'count': ''},to=message['room'])
            emit('my_response', {'data': 'Join Room to Play 🎮', 'count': ''},to=message['room'])
            emit('my_num', {'player2sid':request.sid, 'data': playerBuffer_sid[message['room']].index(request.sid), 'other':playerBuffer_sid[message['room']][0]},to=message['room'])
            print(request.sid, playerBuffer_sid[message['room']].index(request.sid))
        else:
            playerBuffer_num[message['room']] -= 1
            emit('my_response', {'data': 'Room Full❗❗', 'count': ''},to=message['room'])
    else:
        playerBuffer_num[message['room']] = 1
        playerBuffer_sid[message['room']] = [request.sid]
        join_room(message['room'])
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
            {'data': 'In rooms: ' + ', '.join(rooms()),
            'count': session['receive_count']},to=message['room'])
        print(request.sid, playerBuffer_sid[message['room']].index(request.sid))
    print(playerBuffer_num)
    print(playerBuffer_sid)


@socketio.event
def hit(message):
    print(message)
    emit('hitting',
         {'data': 1, 'enemy': message['enemy']},
         to=message['room'])


    

@socketio.event
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.event
def connect():
    global thread
    # if(len(playerBuffer)>2):
    #     return
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})
    emit('first_connect', {'mysid':request.sid})
    # playerBuffer.add(request.sid)
    # print(playerBuffer)
    # currentSocketId = request.namespace.socket.sessid
    # print(str(request.namespace.socket.sessid))
    # print(Fore.GREEN+"[INFO]" + "sid：",request.sid)
    print("\033[1;32m[INFO]\033[0m" + " sid：",request.sid)
    # if(len(playerBuffer)==2):
    #     emit('my_response', {'data': 'Two Player Enter.', 'count': ''})
    #     emit('my_response', {'data': 'Join Room to Play 🎮', 'count': ''})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)

# -*- coding: UTF-8 -*-
from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
import os
from utils import *

app = Flask(__name__)
socketio = SocketIO(app)

try:
    REDIS_URL = os.environ.get("REDIS_URL")
except:
    REDIS_URL = None

r = Redis(REDIS_URL)

@app.route('/')
def index():
    roomID = request.args.get('room', None)
    return render_template('index.html', autoConnect=roomID)

@socketio.on('createRoom')
def createRoom(data):
    try:
        maxRound = int(data['maxRound'])
        if maxRound < 1:
            raise Exception()
    except:
        maxRound = 1

    roomID = generator()
    playerSessionID = request.sid

    rooms = r.getRooms()
    rooms[roomID] = {'players': [playerSessionID], 'rounds': [], 'maxRound': maxRound}
    r.setRooms(rooms)

    emit('roomCreated', {'roomID': roomID})

@socketio.on('joinRoom')
def joinRoom(data):
    roomID = data['roomID']
    rooms = r.getRooms()

    if roomID not in rooms:
        emit('failedToJoin',  {'error': f'ოთახის ნომერი {roomID} არ არსებობს'})
        return

    if len(rooms[roomID]['players']) == 2:
        emit('failedToJoin',  {'error': f'ოთახი {roomID} სავსეა'})
        return

    playerSessionID = request.sid

    if playerSessionID == rooms[roomID]['players'][0]:
        emit('failedToJoin',  {'error': 'საკუთარ თავს ვერ ეთამაშები'})
        return
 
    rooms[roomID]['players'].append(playerSessionID)

    for player in rooms[roomID]['players']:
        emit('joined', {'roomID': roomID}, room=player)

    r.setRooms(rooms)

@socketio.on('play')
def play(data):
    playerSessionID = request.sid
    roomID = data['roomID']
    rooms = r.getRooms()

    if len(rooms[roomID]['players']) != 2:
        emit('failedToPlay',  {'error': 'თქვენ არ ხართ ამ ოთახის წევრი'})
        return

    if playerSessionID != rooms[roomID]['players'][0] and playerSessionID != rooms[roomID]['players'][1]:
        emit('failedToPlay',  {'error': 'თქვენ არ ხართ ამ ოთახის წევრი'})
        return
         
    move = data['move']

    if move != rock and move != paper and move != scissors:
        emit('failedToPlay',  {'error': 'არასწორი მოქმედება'})
        return

    if len(rooms[roomID]['rounds']) == 0 or len(rooms[roomID]['rounds'][-1]) == 3: # start new round
        rooms[roomID]['rounds'].append({playerSessionID: move})
    else:
        if len(rooms[roomID]['rounds'][-1]) == 0:
            rooms[roomID]['rounds'][-1][playerSessionID] = move
        else:
            if playerSessionID in rooms[roomID]['rounds'][-1]:
                emit('failedToPlay',  {'error': 'სვლა უკვე გააკეთეთ, დაელოდეთ მოწინააღმდეგეს'})
                return
            else:
                otherPlayerMove = list(rooms[roomID]['rounds'][-1].values())[0]
                otherPlayerSessionID = list(rooms[roomID]['rounds'][-1].keys())[0]

                result = RockPaperScissors({'id': playerSessionID, 'move': move}, {'id': otherPlayerSessionID, 'move': otherPlayerMove})

                rooms[roomID]['rounds'][-1]['winner'] = result
                rooms[roomID]['rounds'][-1][playerSessionID] = move # just for logging

                if len(rooms[roomID]['rounds']) == rooms[roomID]['maxRound']:
                    wins = [i['winner'] for i in rooms[roomID]['rounds']]
                    p1wins = wins.count(playerSessionID)
                    p2wins = wins.count(otherPlayerSessionID)

                    emit('gameComplete',  {
                        'result': f"თამაში დასრულდა ანგარიშით {p1wins} - {p2wins}" + (f", თქვენ {'გაიმარჯვეთ' if p1wins > p2wins else 'დამარცხდით'}" if p1wins != p2wins else "")
                        },
                    room=playerSessionID)

                    emit('gameComplete',  {
                        'result': f"თამაში დასრულდა ანგარიშით {p1wins} - {p2wins}" + (f", თქვენ {'გაიმარჯვეთ' if p1wins < p2wins else 'დამარცხდით'}" if p1wins != p2wins else "")
                        },
                    room=otherPlayerSessionID)

                    rooms[roomID]['rounds'] = [] # match restarts
                else:
                    if result == None:
                        emit('roundComplete',  {'result': 'რაუნდი ფრედ დასრულდა'}, room=playerSessionID)
                        emit('roundComplete',  {'result': 'რაუნდი ფრედ დასრულდა'}, room=otherPlayerSessionID)
                    else:
                        if result == playerSessionID:
                            emit('roundComplete',  {f'result': 'რაუნდი დასრულდა თქვენი გამარჯვებით'}, room=playerSessionID)
                            emit('roundComplete',  {f'result': 'რაუნდი დასრულდა თქვენი დამარცხებით'}, room=otherPlayerSessionID)
                        else:
                            emit('roundComplete',  {f'result': 'რაუნდი დასრულდა თქვენი გამარჯვებით'}, room=otherPlayerSessionID)
                            emit('roundComplete',  {f'result': 'რაუნდი დასრულდა თქვენი დამარცხებით'}, room=playerSessionID)
    r.setRooms(rooms)

# socketio.run(app)
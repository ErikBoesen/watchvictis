from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
import tbapi
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

TEAM = 1418

tba = tbapi.TBAParser(TEAM, 'watchvictis', 0.1)

def get_tba_data():
    data = {}
    for i in tba.get_team_events(TEAM):
        if datetime(i.start_date) < datetime.now() and datetime.now() < datetime(i.end_date):
            event = i
            break
        event = {}
    event['matches'] = tba.get_team_event_matches(TEAM, event.key)
    return data


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('event', namespace='/req')
def message(message):
    emit('response', get_tba_data())


@socketio.on('connect', namespace='/req')
def connect():
    emit('response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/req')
def disconnect():
    print('Client disconnected.')


if __name__ == '__main__':
    socketio.run(app)

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, disconnect
from datetime import datetime
import tbapy

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

TEAM = 1418

tba = tbapy.TBA('%s:watchvictis:0.1' % TEAM)

current_data = None


def get_tba_data(debug=False):
    """
    Fetch required data from The Blue Alliance and compile it.

    :param debug: When True, provide data for a predefined event. For debugging when an event isn't going on.
    :returns: Single JSON object with all data necessary for operation.
    """
    if debug:
        data = tba.event('2016vahay')
    else:
        data = {}
        now = datetime.now()
        for i in tba.team_events(TEAM, now.year):
            start = list(map(int, i['start_date'].split('-')))
            end = list(map(int, i['end_date'].split('-')))
            if datetime(start[0], start[1], start[2]) < now and now < datetime(end[0], end[1], end[2]):
                data = i
                break
    if data is not {}:
        matches = sorted(tba.team_matches(TEAM, data['key']), key=lambda match: (['qm', 'qf', 'sf', 'f'].index(match['comp_level']), match['match_number']))
        for i in range(0, len(matches)):
            matches[i] = {
                'comp_level': matches[i]['comp_level'],
                'match_number': matches[i]['match_number'],
                'teams': {
                    'red':  list(map(lambda key: key[3:], matches[i]['alliances']['red']['teams'])),
                    'blue': list(map(lambda key: key[3:], matches[i]['alliances']['blue']['teams']))
                }
            }
            data = {
                'matches': matches,
                'webcast': data['webcast'],
            }
    return data


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    global current_data
    while True:
        count += 1
        current_data = get_tba_data(True)
        socketio.emit('data',
                      current_data,
                      namespace='/req')
        socketio.sleep(30)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/req')
def connect():
    global thread
    # Prevent opening of multiple threads at one time.
    # This is annoying for the end-user, but we don't want to be fetching redundant TBA data for every single person viewing the app.

    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('data', current_data)

@socketio.on('disconnect', namespace='/req')
def disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)

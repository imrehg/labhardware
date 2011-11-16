import sys
sys.path.append('../../drivers')
import bottle
from bottle import route, view, static_file, post, get, request, run
import novatech409b as nova

bottle.debug(True)

synth = nova.N409B()

@route('/static/<path:path>')
def callback(path):
    return static_file(path,  root='./static/')

@route('/')
@view('aom')
def main():
    return dict()

@post('/setfreq/<channel>/<frequency>')
def setfreq(channel, frequency):
    result = synth.setFreq(channel, frequency)
    return result

@post('/setlevel/<channel>/<level>')
def setfreq(channel, level):
    result = synth.setLevel(channel, level)
    return result

@post('/setphase/<channel>/<phase>')
def setphase(channel, phase):
    result = synth.setPhase(channel, phase)
    return result

@get('/settings/')
@get('/settings/<channel>')
def settings(channel=None):
    """ Return settings for all or a given channel """
    try:
        channel = int(channel)
    except TypeError:
        channel = None
    if channel not in [0, 1, 2, 3]:
        channel = None

    channels = synth.getChannels()
    res = channels if channel is None else channels[channel]
    return res

run(host='localhost', port=8080)

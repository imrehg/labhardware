import sys
sys.path.append('../../drivers')
import bottle
from bottle import route, view, static_file, post, get, run
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

run(host='localhost', port=8080)

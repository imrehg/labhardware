import sys
sys.path.append('../../drivers')
import bottle
from bottle import route, view, static_file, post, get, request, run
import novatech409b as nova
import time

bottle.debug(False)

synth = nova.N409B()

@route('/static/<path:path>')
def callback(path):
    return static_file(path,  root='./static/')

@route('/')
@view('sweeper')
def main():
    return dict()

@post('/sequence')
def setsequence():
    f = request.forms.get
    params = {}
    try:
        params['sfreq0'] = float(f('sfreq0'))
        params['sfreq1'] = float(f('sfreq1'))
        params['ffreq0'] = float(f('ffreq0'))
        params['ffreq1'] = float(f('ffreq1'))
        params['repeat'] = True if f('repeat') == 'true' else False
        params['stepsize'] = int(f('stepsize'))
        params['totaltime'] = float(f('totaltime'))
        start = time.time()
        synth.sweep(params)
        total = time.time() - start
        ret = {'result': 'OK', 'totaltime': total}
    except:
        ret = {'result': 'ERROR'}
    return ret

@get('/trigger')
def sendtrigger():
    """ Software trigger send """
    synth.trigger()
    return {'result': 'OK'}

port = 8900
print("**** RUNNING ON PORT %d ****" %(port))
run(host='0.0.0.0', port=port)

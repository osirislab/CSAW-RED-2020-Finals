from flask import Flask, render_template, redirect, session, make_response, request
import itsdangerous
import time
import datetime
import json
import random
import uuid
import secrets
import binascii
import struct

class SingleUser:
    def __init__(self):
        self.uuid = None
        self.scid = None
        self.orig_time = None
        self.flag_time = None
        self.last_nonce = '0'

app = Flask(__name__)
app.secret_key = "adfasdfasdfasdfs"
master_dict = {}

THREE_MINUTES_IN_SECONDS = 180

ML_A = ['attitude', 'power', 'temperatures', 'pointing', 'comms', 'radios', 'panels', 'payload']
ML_B = ['good', 'bad','off-nominal', 'normal', 'nominal', 'abnormal', 'excellent', 'constraint satisfied']
ML_C = ['going to', 'avoiding', 'cancelling', 'establishing']
ML_D = ['next contact', 'next manuever', 'sun-pointing', 'pointing', 'charging']
FLAG = "flag{gr0und_c0ntr01_2_mJ0r_T0m_c0mmenc1nG_c0und0wn_3ngin3s_0n}"

def encode_time(scid, time):
    timestr = str(time).encode('ascii')
    key = scid.bytes
    key_adj = key * ((len(timestr) // len(key) + 1)) 
    return binascii.hexlify(bytes([a^b for a,b in zip(timestr, key_adj)]))

def decode_time(scid, time):
    timestr = binascii.unhexlify(time)
    key = scid.bytes
    key_adj = key * ((len(timestr) // len(key) + 1)) 
    return float(bytes([a^b for a,b in zip(timestr, key_adj)]).decode('ascii'))

def generate_su():
    su = SingleUser()
    su.uuid = uuid.uuid4()
    su.scid = uuid.uuid4()
    su.orig_time = time.time() + THREE_MINUTES_IN_SECONDS
    su.flag_time = su.orig_time + THREE_MINUTES_IN_SECONDS
    return su

def generate_flavor_message():
    timestamp = datetime.datetime.utcfromtimestamp(time.time())
    madlibs = "{} {}, {} {}".format(random.choice(ML_A).upper(),random.choice(ML_B),random.choice(ML_C),random.choice(ML_D))
    message = "{}: {}:{}".format(timestamp, binascii.hexlify(struct.pack('H', random.randint(0,0xffff))).decode('ascii').upper(), madlibs)
    return message

@app.route("/")
def index():
    if not 'id' in session:
        su = generate_su()
        session['id'] = su.uuid
        master_dict[su.uuid] = su
    elif not session['id'] in master_dict.keys():
        su = generate_su()
        session['id'] = su.uuid
        master_dict[su.uuid] = su
    else:
        return render_template('index.html', value=master_dict[session['id']].scid)
    res = make_response(render_template('index.html', value=su.scid))
    res.set_cookie('scid', binascii.hexlify(su.scid.bytes).decode('ascii'), 60*60*2)
    res.set_cookie('enctime', encode_time(su.scid,su.orig_time).decode('ascii'), 5)
    print(encode_time(su.scid, su.flag_time+15))
    res.set_cookie('endtime', str(int(su.orig_time)).encode('ascii'), 60*60*2)
    return res

@app.route("/take_step", methods=["POST"])
def step():
    try:
        su = master_dict[session['id']]
    except:
        su = SingleUser()
        su.uuid = uuid.uuid4()
        su.scid = uuid.uuid4()
        su.orig_time = time.time() + THREE_MINUTES_IN_SECONDS
        su.flag_time = su.orig_time + THREE_MINUTES_IN_SECONDS
        session['id'] = su.uuid
        master_dict[su.uuid] = su
        
    prev = request.form
    prev_nonce = prev['nonce']
    new_nonce = secrets.token_hex(16)
    if prev_nonce != su.last_nonce and prev_nonce != 'badnonce':
        print("nonce mismatch!! {}!={} {}/{}".format(prev_nonce, su.last_nonce, type(prev_nonce), type(su.last_nonce)))
        su.last_nonce = new_nonce
        data = {"nonce":new_nonce, "message":"last nonce was bad! NO INFO FOR YOU!"}
        return json.dumps(data)
    
    su.last_nonce = new_nonce
    enctime = prev['enctime']
    real_enctime = 0
    try:
        real_enctime = decode_time(su.scid, enctime)
    except:
        print("bad enctime: {}".format(enctime))
        if (enctime != '0'):
            data = {"nonce":new_nonce, "message":"Session may be invalid"}
            return json.dumps(data)
        else:
            data = {"nonce":new_nonce, "message":"Establishing session"}
            return json.dumps(data)


    if real_enctime < time.time():
        data = {"nonce":new_nonce, "message":"Out of contact. No further contact scheduled."}
        return json.dumps(data)
    if time.time() > su.flag_time:
        data = {"nonce":new_nonce, "message":FLAG}
        return json.dumps(data)

    print("Nonce: {} Enctime: {}".format(prev_nonce, real_enctime))
    data = {"nonce":new_nonce, "message":generate_flavor_message()}
    return json.dumps(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
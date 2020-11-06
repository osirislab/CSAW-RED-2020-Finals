import random
import array
import crcmod
import copy
import uuid
import json
import binascii

from flask import Flask, render_template, request, session

crc16 = crcmod.predefined.mkPredefinedCrcFun('crc-16')
app = Flask(__name__)
app.secret_key = 'asdfasdfasdfasdf'
TABLE_BIT_SIZE = 4096
FLAG = 'flag{w311_i_gue55_y0u_c4n_d0_a_fl1p}'
TOO_MANY_CHANGES = 'errorstringtoomanychanges'
MAX_CHANGE_COUNT = 8

table_holder = {}
with open('index.html','r') as page:
    home = page.read()

class ScTable:
    def __init__(self, bit_size, num_flips=3):
        self.target_table = [random.randint(0,255) for i in range(bit_size//8)]
        self.table = self.generate_flipped_table(num_flips)
        self.crc_count = 0
        self.change_count = 0
        self.length = len(self.target_table)
    
    def generate_flipped_table(self, num_flips):
        local = copy.deepcopy(self.target_table)
        for _ in range(num_flips):
            byte = random.randint(0,len(local)-1)
            bit = random.randint(0,7)
            flip_num = 1 << bit
            local[byte] ^= flip_num
        return local
    
    def change_byte(self, index, b):
        self.change_count += 1
        try:
            self.table[index] = int(b)
        except:
            return False
        if self.change_count > MAX_CHANGE_COUNT:
            return TOO_MANY_CHANGES
        return True
    
    def get_crc(self, i, l):
        self.crc_count += 1
        a = array.array("B")
        a.fromlist(self.table[i:i+l])
        return crc16(a.tobytes())
    
    def is_success(self):
        return self.table == self.target_table
    
    def get_target_table(self):
        return binascii.hexlify(bytes(self.target_table)).decode('ascii')

@app.route('/homepage')
def homepage():
    return home

@app.route('/')
def index():
    u = uuid.uuid4()
    session['uuid'] = str(u)
    table_holder[str(u)] = ScTable(TABLE_BIT_SIZE)
    print(table_holder)
    return json.dumps({"message": "SCID: {}.  Make sure to include your session token every time.".format(u), "scid":str(u)})

@app.route('/table_status', methods=['GET'])
def get_status():
    print(request.args)
    uuid = request.args['scid']
    if not 'uuid' in session and not uuid:
        return json.dumps({"message":"You don't have a session. Go to / and get one."})
    if not uuid in table_holder.keys():
        print(table_holder)
        return json.dumps({"message":"You don't have a VALID session. Go to / and get one."})
    table = table_holder[uuid]
    if table.is_success():
        return json.dumps({"message":"Congratulations.  Have a flag. {}".format(FLAG)})
    else:
        return json.dumps({"message":"Invalid table detected."})

@app.route('/table_target', methods=['GET'])
def get_target():
    print(request.args)
    uuid = request.args['scid']
    if not 'uuid' in session and not uuid:
        return json.dumps({"message":"You don't have a session. Go to / and get one."})
    if not uuid in table_holder.keys():
        print(table_holder)
        return json.dumps({"message":"You don't have a VALID session. Go to / and get one."})
    table = table_holder[uuid]
    return json.dumps({"table":table.get_target_table(), "length":table.length})

@app.route('/change_byte', methods=['POST'])
def change_byte():
    data = request.json
    print(data)
    uuid = data['scid']
    # if not 'uuid' in session:
    #     return json.dumps({"message":"You don't have a session. Go to / and get one."})
    if not uuid in table_holder.keys():
        return json.dumps({"message":"You don't have a VALID session. Go to / and get one."})
    table = table_holder[uuid]
    index = data['index']
    value = data['value']
    status = table.change_byte(index, value)
    if status == TOO_MANY_CHANGES:
        del table_holder[uuid]
        return json.dumps({"message":"Too many changes.  Goodbye."})
    if status:
        return json.dumps({"message":"Changed byte {} to {}".format(index, value)})
    else:
        return json.dumps({"message":"Failed to change byte."})

@app.route('/crc', methods=['POST'])
def crc_section():
    data = request.json
    uuid = data['scid']
    if not uuid in table_holder.keys():
        return json.dumps({"message":"You don't have a VALID session. Go to / and get one."})
    start = data['start']
    count = data['count']
    table = table_holder[uuid]
    try:
        crc = table.get_crc(start, count)
    except:
        return json.dumps({"message":"Error. Unable to give crc."})
    return json.dumps({"crc":crc, "start":start, "count":count, "message":"Successfully got CRC."})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
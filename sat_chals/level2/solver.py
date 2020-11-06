import requests
import crcmod
import json
import struct
import array
import binascii

crc16 = crcmod.predefined.mkPredefinedCrcFun('crc-16')

HOST = 'http://192.168.109.141:5000'

def get_id():
    url = "{}/".format(HOST)
    r = requests.get(url)
    d = r.json()
    return d['scid']

def get_table(scid):
    url = "{}/{}".format(HOST, 'table_target')
    params = {"scid":scid}
    r = requests.get(url, params=params)
    d = r.json()
    table = d['table']
    length = d['length']
    return table,length

def remote_crc(scid, i, l):
    url = "{}/{}".format(HOST, "crc")
    data = {'scid':scid, 'start':i,'count':l}
    r = requests.post(url, json=data)
    d = r.json()
    return d['crc']

def local_crc(table, i, l):
    a = array.array("B")
    a.fromlist(table[i:i+l])
    return crc16(a.tobytes())


def find_byte_from_crc(target_crc):
    for i in range(256):
        if crc16(bytearray([i])) == target_crc:
            return i
    return None

def find_flips(table, scid, l=None, i=0):
    if not(l):
        l = len(table)
    target_crc = local_crc(table, i, l)
    current_crc = remote_crc(scid, i, l)
    if target_crc == current_crc:
        return True
    elif l == 1:
        res = find_byte_from_crc(target_crc)
        print("found a flip at {} -> {}".format(i, res))
        return [(i,res)]
    else:
        left = find_flips(table, scid, l=l//2, i=i)
        if left == True:
            left = []
        right = find_flips(table, scid, l=l//2, i=i+l//2)
        if right == True:
            right = []
        return left+right
    print('fell through...')
    return []
    
def flip_on_remote(scid, index, value):
    url = "{}/{}".format(HOST, "change_byte")
    data = {'scid':scid, 'index':index, 'value':value}
    r = requests.post(url, json=data)
    return r.text

def check_success(scid):
    url = "{}/{}".format(HOST, 'table_status')
    params = {"scid":scid}
    r = requests.get(url,params=params)
    return r.text

if __name__ == '__main__':
    scid = get_id()
    print("Solving for scid: {}".format(scid))
    t, l = get_table(scid)
    t = binascii.unhexlify(t)
    a = array.array("B")
    a.frombytes(t)
    t = a.tolist()
    print("Table len: {}".format(l))
    full_crc = remote_crc(scid, 0, l)
    print("Table crc: {}".format(full_crc))
    flips = find_flips(t, scid)
    for f in flips:
        print("flip: {}".format(f))
        flip_on_remote(scid, f[0], f[1])
    status = check_success(scid)
    print("wow: {}".format(status))
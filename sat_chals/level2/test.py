import random
import struct
import array
import binascii
import copy
import crcmod

TABLE_BIT_SIZE = 4096

crc16 = crcmod.predefined.mkPredefinedCrcFun('crc-16')

crc_count = 0

def gen_table():
    r = random.getrandbits(TABLE_BIT_SIZE)
    r = [random.randint(0,255) for i in range(TABLE_BIT_SIZE//8)]
    for x in r:
        assert x <= 0xff
    print(len(r))
    return r

def encode_table_to_hex(t):
    a = array.array("B")
    a.fromlist(t)
    return binascii.hexlify(a.tobytes())

def flipper(t, num_to_flip):
    local = copy.deepcopy(t)
    for i in range(num_to_flip):
        byte = random.randint(0,len(t)-1)
        bit = random.randint(0,7)
        flip_num = 1 << bit
        # print("Flipping {}:{}".format(byte, bit))
        # print(local[byte])
        local[byte] ^= flip_num
        # print(local[byte])
    return local

def arb_crc(table, first, length):
    global crc_count
    crc_count += 1
    a = array.array("B")
    a.fromlist(table[first:first+length])
    return crc16(a.tobytes())

def find_byte_from_crc(target_crc):
    for i in range(256):
        if crc16(bytearray([i])) == target_crc:
            return i
    return None

def find_flips(t, q, i=0, l=None, current_index=0):
    if not l:
        l = len(t)
    target = arb_crc(t, i, l)
    current = arb_crc(q, i, l)
    if (target == current):
        return q
    elif l == 1:
        res = find_byte_from_crc(target)
        print("found flip at {}, switched back to {}".format(current_index, res))
        if res is None:
            raise RuntimeError("wtf: {}".format(target))
        return [res]
    else:
        left = find_flips(t[0:l//2], q[:l//2], i=0, l=l//2, current_index=current_index)
        right = find_flips(t[l//2:], q[l//2:], i=0, current_index=current_index + l//2)
        return left + right

    return None

def dummy_flips(t,q):
    flips = []
    for x,y,z in zip(t,q,range(len(t))):
        if x != y:
            flips.append(z)
            print("flip at {}: {}->{}".format(z, x, y))
    return flips



if __name__ == '__main__':
    t = gen_table()
    flipped = flipper(t, 18)
    h = encode_table_to_hex(t)
    fh = encode_table_to_hex(flipped)
    # print(h)
    # print(fh)
    a = arb_crc(t, 0, len(t))
    b = arb_crc(flipped, 0, len(t))
    print(a)
    print(b)
    dummy_flips(t,flipped)
    crc_count = 0
    fixed = find_flips(t,flipped)
    print(fixed)
    print(dummy_flips(t, fixed))
    print("took {} crcs".format(crc_count))
#!/usr/bin/python3

from pwn import *
import binascii

local = True
context.log_level = 'error'


#### Functions to interact with the program

def initialize_connection(local):
    if local:
        p = remote('localhost', 5000)
    else:
        p = remote('crypto.red.csaw.io', 5000)
    return p

def get_ct():
    p.recvuntil("> ")
    p.send("2\n")
    p.recvuntil("is:\r\n\r\n")
    pwd = p.recvuntil("\r\n").strip()
    pwd = binascii.unhexlify(pwd)
    return(pwd)

def send_ct(p, ct):
    p.recvuntil("> ")
    p.send("1\n")
    p.recvuntil("string:\r\n\r\n> ")
    p.send(binascii.hexlify(ct)+b'\n')

# Here ct is a byte string, the index is the byte that should be modified, and the value is the new value
# as an integer
def modify_byte(ct, index, value):
    tmp = bytearray(ct)
    tmp[index] = value
    return bytes(tmp)

def padding_is_at_index(ct, index):
    # Modifying the previous ciphertext block but the indexing is on the block of
    # decrypted plaintext we want to change
    new_ct = modify_byte(ct, index-16, ct[index-16]^0xff)
    if padding_is_valid(new_ct): # Means that modifying this byte did not change the padding bytes
        return False
    else:
        return True

def padding_is_valid(ct):
    p = initialize_connection(local)
    send_ct(p, ct)
    p.recvline()
    result = p.recv(6)
    if (result == b'That\'s'):
        p.close()
        p.wait_for_close()
        return True
    elif (result == b'Error:'):
        p.close()
        p.wait_for_close()
        return False
    else:
        print("Either there's an error, or we should have the flag.")
        p.interactive()

def get_padding_byte(ct):
    for i in range(-16,0):
        if padding_is_at_index(ct, i):
            print("The padding byte is " + hex(abs(i)))
            return(abs(i))
    print("Error: did not find any padding bytes in this block.")
    exit(0)


#### Decryption functions

## Assumes that I am already working with the last two blocks of ciphertext
## So this takes two blocks of ciphertext, the index is for the second block,
## we assume that the index is greater than the padding
## ct is a bytestring, known_pt is a bytestring, padding is a byte
## Return value: the guessed byte
def guess_next_plaintext_byte(ct, known_pt, padding):
    ct = bytearray(ct)
    assert(len(known_pt) >= padding)
    assert(len(known_pt) < 16) # Otherwise we don't need to guess the next byte in the block
    index = 16 - len(known_pt) - 1
    required_padding = len(known_pt) + 1
    for i in range(len(known_pt)):
        ct[-16-(i+1)] ^= (known_pt[-(i+1)] ^ required_padding)
    guess = 0
    original_ct = ct[index]
    while guess < 256:
        ct[index] = original_ct ^ guess ^ required_padding
        if(padding_is_valid(bytes(ct))):
            return bytes([guess])
        guess+=1
    print("Error in guess_next_plaintext_byte: no guess worked.")
    exit(0)

# This requires two blocks of ciphertext, and I decrypt the second.
# For the last block, set padding to a number. Default is zero.
def decrypt_plaintext_block(ct, padding=0):
    known_pt = (chr(padding)*padding).encode("utf-8")
    while len(known_pt) < 16:
        known_pt = guess_next_plaintext_byte(ct, known_pt, padding) + known_pt
        print("In decrypt_plaintext_block: decrypted " + str(known_pt) + " (length = " + str(len(known_pt)) + ")")
    return known_pt

## Now I have all the ingredients for destruction: determining 
## the padding, guessing a byte, and decrypting a plaintext block.
## Now I want to decrypt everything.
def decrypt_entire_message(ct):
    assert(len(ct)%16==0)
    n_blocks = len(ct)/16
    assert(n_blocks > 1)
    pt = b''
    padding_byte = get_padding_byte(ct)
    decrypted_block_count = 0
    pt = decrypt_plaintext_block(ct[-32:],padding=padding_byte) + pt
    print("In decrypt_entire_message: decrypted last block and pt = " + str(pt))
    decrypted_block_count += 1
    while(decrypted_block_count < (n_blocks-1)):
        #print("ciphertext to decrypt: " + str())
        pt = decrypt_plaintext_block(ct[-(16*(decrypted_block_count+2)):-(16*(decrypted_block_count))],padding=0) + pt
        decrypted_block_count += 1
        print("In decrypt_entire_message: decrypted " + str(decrypted_block_count) + " blocks and pt = " + str(pt))
    return(pt)


#### Encryption Functions

# Helper function. Assume inputs are two byte strings.
def xor_two_blocks(A,B):
    A_bytes = bytearray(A)
    B_bytes = bytearray(B)
    assert(len(A_bytes)==len(B_bytes))
    result = bytearray()
    for i in range(len(A_bytes)):
        result.append(A_bytes[i]^B_bytes[i])
    return(bytes(result))

def pad(m):
    padding = 16 - len(m)%16
    padded = m + (chr(padding)*padding).encode("utf-8")
    return(padded)

def unpad(padded):
    padding = padded[-1]
    m =  padded[:-1*padding]
    return(m)

## Take in a ciphertext block of length 2 and optionally the plaintext of the second block.
## Decrypt the second block if necessary, replace the first block with 
## the plaintext of the second block xored with the desired plaintext for the first block,
## and return the resulting ciphertext (both blocks).
def encrypt_block(ct, new_pt, old_pt=None):
    assert(len(ct) == 32)
    assert(len(new_pt) == 16)
    if(old_pt is not None):
        assert(len(old_pt) == 16)
    if old_pt is None:
        # I know the padding if and only if I know the plaintext in advance
        old_pt = decrypt_plaintext_block(ct, padding=0) 
    result = xor_two_blocks(ct[:16],xor_two_blocks(new_pt,old_pt))
    result += ct[16:]
    return(result)

def encrypt_message(new_pt, ct, last_old_pt_block):
    new_pt = pad(new_pt)
    assert(len(ct)>=32)
    n_blocks_encrypted = 0
    # Throw away all the ciphertext except the last two blocks
    ct = ct[-32:]
    ct = encrypt_block(ct=ct,new_pt=new_pt[-16:],old_pt=last_old_pt_block)
    print("In encrypt_message: one block encrypted and ciphertext = " + ct.hex())
    n_blocks_encrypted += 1
    while(n_blocks_encrypted < len(new_pt)/16):
        tmp_ct_null_IV = bytes(16)+ct[:16]
        tmp_ct = encrypt_block(ct=tmp_ct_null_IV, new_pt = new_pt[-16*(n_blocks_encrypted+1):-16*n_blocks_encrypted],old_pt=None)
        ct = tmp_ct[:16] + ct
        n_blocks_encrypted += 1
        print("In encrypt_message: " + str(n_blocks_encrypted) + " blocks encrypted and ciphertext = " + ct.hex())
    #ct = binascii.unhexlify("53a2095dac756e747d33828c531af0399581d815136749ccc7faa07ad699a0ebddf73947848da484f77dbed379f196f7e20bafdb251d827665dc1fec735702b958c5b92a9779304b5e89a5c459cc4fd8")
    return(ct)


## Get the initial cyphertext
p = initialize_connection(local)
ct = get_ct()
p.close()
p.wait_for_close()

## Decrypt the ciphertext
old_m = decrypt_entire_message(ct) # Got it, yay! 
print("old plaintext = " + str(old_m))

## Encrypt an entire message
flag_hash = unpad(old_m)[-32:]
print("Old flag hash = " + str(flag_hash))
new_m = b'Password:Strahd, hash of flag: ' + flag_hash
print("new_m = " + str(new_m))
new_ct = encrypt_message(new_m,ct,last_old_pt_block=old_m[-16:])

## Profit
print("This should give us the flag:")
p = initialize_connection(local)
send_ct(p, new_ct)
p.interactive()
#!/usr/bin/python3
from Crypto.Cipher import AES
import binascii
import hashlib
import os
import sys

flag = open('./flag.txt', 'r').read().strip()
key = open('./key', 'r').read().strip()
last_password = open('./password.txt', 'r').read().strip()

#print("flag = " + flag)
#print("flag length: " + str(len(flag)))

def get_last_password():
    flag = open('./flag.txt', 'r').read().strip().encode("utf-8")
    # Want the padding to be more than 0x01 because that's instructive to decrypt
    m = b'Password:' + last_password.encode("utf-8") + b', flag hash: '
    m += hashlib.md5(flag).hexdigest().encode("utf-8")
    #print("Last password = " + str(m))
    return(m)

def pad(m):
    padding = 16 - len(m)%16
    padded = m + (chr(padding)*padding).encode("utf-8")
    #print("padded message: " + padded)
    return(padded)

def unpad(padded):
    #print("padded is of class " + str(padded.__class__))
    padding = padded[-1]
    #print("In unpad: padding = " + str(padding))
    m =  padded[:-1*padding]
    #print("In unpad: unpadded message = " + str(m))
    return(m)

def valid_padding(pt):
    padding = pt[-1]
    #print("padding = " + str(padding))
    #print("padding type = " + str(padding.__class__))
    #print("pt type = " + str(pt.__class__))
    valid = True
    for i in range(padding):
        if pt[-(i+1)]!=padding:
            print("i = " + str(i) + " and padding is invalid")
            valid = False
            break
    return valid

def encrypt(pt):
    IV = "Best_StarWars:IV"
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, IV)
    ct = (IV.encode("utf-8") + cipher.encrypt(pad(pt))).hex()
    #print(ct)
    return(ct)
    #print("ct class: " + str(ct.__class__))
    #print(str(IV.encode("utf-8").__class__))
    #print(str(ct.hex().__class__))
    #ct = IV.encode("utf-8") + ct
    #print("ct: " + str(ct))
    #print("ct: " + IV.encode("utf-8") + ct.hex())

def decrypt(ct):
    ct_bytes = binascii.unhexlify(ct)
    IV = ct_bytes[0:16]
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, IV)
    pt = cipher.decrypt(ct_bytes[16:])
    #print("plaintext = " + str(pt))
    return(pt)

  #cipher = AES.new(key.decode('hex'), AES.MODE_CBC, m[0:32].decode("hex"))
  #return cipher.decrypt([32:].decode("hex"))

def get_selection():
    print("Enter your selection:")
    print("   1) Unlock this week\'s secret chest")
    print("   2) Retrieve a password reminder")
    print("   3) Return to your plane of existence")
    print("> ", end='')
    selection = input()
    if selection in list('123'):
        print("")
        return selection
    else:
        print("Error: Invalid selection.")
        exit(0)

def unlock_chest(ct):
    pt = decrypt(ct)
    #print("In unlock_chest: pt = " + str(pt))
    if valid_padding(pt):
        unpadded = unpad(pt)
        #print("In unlock_chest: the plaintext is " + str(unpadded))
        #print("flag = " + str(flag) + "and flag type = " + str(flag.__class__))
        #print(unpadded[31:])
        #print(hashlib.md5(flag.encode("utf-8")).hexdigest().encode("utf-8"))
        if(unpadded[0:15]==b'Password:Strahd' and \
           unpadded[31:]==hashlib.md5(flag.encode("utf-8")).hexdigest().encode("utf-8")):
            print("Welcome Leomund! Your flag is " + str(flag))
            exit(0)
        else:
            print("That\'s not this week\'s password!")
            exit(0)
        #if(unpadded[31:]==hashlib.md5(flag.encode("utf-8")).hexdigest().encode("utf-8")):
        #    print("You got the hash!")
        #if(unpadded[0:31]==b'Password:icanspell, flag hash: '):
        #    print("You got the password!")
        #return unpadded
    else:
        print("Error: invalid padding")
        exit(0)


def main():
    # Start by flushing output
    #sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stdout.flush()

    print("***** Leomund's Secret Chest *****\n")
    print("   Welcome back to the interface for your secret chest, Leomund.")
    print("Only you would store your valuables in an extradimensional space.")
    print("If you've forgotten this week\'s password, this interface can")
    print("give you last week\'s as a reminder. Just use your key to")
    print("decrypt it and jog your memory.")
    print("   P.S. If you're not Leomund, good luck trying to unlock my chest")
    print("without the key!\n")
    while(1):
        selection = int(get_selection())
        if selection == 1:
            print("Enter your ciphertext as a hex string:\n")
            ct = input("> ")
            print("")
            pt = unlock_chest(ct)
            #print("The plaintext is " + str(pt))
        elif int(selection) == 2:
            #print("got selection 2\n")
            pt = get_last_password()
            ct = encrypt(pt)
            print("Last week's encrypted password is:\n\n" + str(ct) + "\n")
            #print("The length of that is " + str(len(str(ct))))
        elif int(selection) == 3:
            print("Poof!\n")
            exit(0)

main()
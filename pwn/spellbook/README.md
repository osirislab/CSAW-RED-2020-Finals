
# Spellbook

This challenge is an x86-64 ELF binary with full RELRO protection and PIE enabled (i.e. all protections enabled). It's stack-based.


*   *   *   S P O I L E R S   F O L L O W   *   *   *


The program asks the player for a spell name (stored in a 40-byte buffer) and an invocation (stored in a 1200-byte buffer). Both the name and invocation are stored on the stack. Running the program normally triggers a format string vulnerability in printing the invocation when the spell is cast, but that invocation is followed immediately by `exit(0)` so there is no way for the player to overwrite a return address this way. Also full RELRO protection prevents an overwrite of `exit()` in the GOT. 

Disassembling the binary reveals a secret menu option that leaks the location of a variable in the BSS 
section and also prints the spell name with a format string vulnerability there. The catch is, the player can only enter the spell name once, and then a boolean in the BSS section is set to 1, preventing future writes of the spell name. The way around this is for the player, when exploiting this format string vulnerability, to overwrite both the BSS section boolean with a zero and then leak an address with a single format string. That lets the player leak more than one address, allowing fingerprinting of the libc version. It also allows the player to write a ROP chain to the BSS section one byte at a time. The 40-character string length is so restrictive that I had to write shorts to the BSS section to produce the ROP chain, but that works just fine. 

Next is the issue of how to get control of the instruction pointer. The binary is set up so that you never return from the `runRitualCastiing()` function, and a successful invocation is followed by a call to `exit(0)`. The solution is to use the second vulnerability when printing the invocation to overwrite the return address from one of the internal `printf()` functions. I used `printf_positional`. Doing this will require the user to leak a stack address with the first vulnerability (printing the spell name), and then do a little debugging to calculate the appropriate offset to the return address from `printf_positional` when that function gets called to print the invocation. I was able to overwrite the return address from `printf_positional` with a `pop rsp` gadget, and put the address of the ROP chain in the BSS section eight bytes above the return address from `printf_positional`. That leads to the ROP chain and victory.

An alternative approach would involve overwriting the `free_hook` pointer in `libc` with the address of the start of the program (`accessSpellBook`) to get multiple calls to print the format string vulnerability in the invocation buffer. That lets the user create the ROP chain another way, but still requires them to eventually overwrite the return address of `printf_positional`. I let them do plenty of writes from a large buffer storing the invocation, although that isn't strictly necessary and it could have been about half the size that it is for the challenge to be solvable. 

Solving the challenge also requires users to be able to download the libc and then link it to the challenge locally when debugging, in order to get the correct offset for the return address of `printf_positional` for the challenge running on the server. For all these reasons I gave it 400 points.

## Progress as of 11-2: solver working locally, testing it with the `libc` in the Docker container
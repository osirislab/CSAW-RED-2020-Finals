
# Spellbook

This challenge is an x86-64 ELF binary with full RELRO protection and PIE enabled (i.e. all protections enabled). It's stack-based. The player is given the location of a variable in the BSS section and gets one printf() vulnerability for free and a second that runs right before a call to exit(0). They don't get libc with the challenge and have to fingerprint it by reading two libc addresses from the GOT with a single printf call. Then with the second vuln they can overwrite `free_hook` in libc with the address of `main` to set up multiple writes. With the same write they have to change two booleans in the BSS section from TRUE back to FALSE. Each loop back to main moves the stack, so they have to set up their ROP chain in the BSS section and eventually pivot to it to get shell.

## Progress as of 10-31: wrote the challenge, format string vulns exploited properly in the solver, working on the ROP chain portion of the solver
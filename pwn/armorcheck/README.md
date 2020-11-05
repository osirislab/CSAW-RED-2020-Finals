
# armorcheck

This challenge is an x86-64 ELF binary that is a heap overflow challenge. Check your medieval armor at Mordenkainen's magnificent mansion!

This is intended to be the easiest pwnable in finals. It's a straightforward heap overflow. `armor` structs are allocated in the heap, and have the following structure:

```
typedef struct _armor{
    char name[NAMELENGTH]; // will read 20 into temp buffer
    int descriptionLength; 
    char * armorDescription;
} armor;
```

A menu gives users the ability to create an armor reservation, modify the name and description, and view the armor. Deleting an entry is not possible (so no use after free), so many players should immediately think about a heap overflow. 

The twist here is that with most heap overflows, there would be an easy way to overflow either the name or the armor description. Not so here: length checking takes place for both during the update function. But the name gets read into a temporary buffer with `read` that is four bytes longer than NAMELENGTH. Then the length of the string in the temporary buffer gets checked with `strlen` to make sure it's not longer than NAMELENGTH bytes before getting copied over to the `name` array with `memcpy`. So, the vulnerability is that the player can read a string that's 20 bytes long into the temporary buffer, put a null byte in the middle of it to foil `strlen`, and then `memcpy` will copy over the total number of bytes that were read in with `read`. That's a little tricky but it shouldn't really be a challenge for the finalists. I predict everyone will solve this challenge in 30-60 minutes, but we'll see.

Once `name` gets overflowed by four bytes, the `descriptionLength` can be set to something longer, which allows the player to write a long armor description, overflow that buffer, and write into the next `armor` struct on the heap. That allows the `armorDescription` pointer to be overwritten, so that viewing the armor could leak a GOT address and updating the armor could overwrite a GOT address. My solution overwrites the GOT pointer to `strlen` to point to `system`, gets the program to calculate the length of a new name "`/bin/sh\x00`", and that spawns a shell. 

We're not providing source code or libc, they have to reverse engineer the binary and fingerprint libc.

## TODO: Everything works, just need to test it on CTFd. 
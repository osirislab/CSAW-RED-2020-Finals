
# thetrial

This challenge is an x86-64 ELF binary that is a heap shrink-a-free-chunk challenge.

In most ways this is similar to a challenge from the OffSec class. Except that you do not specify the size of a new chunk to be created, you calculate that size by "combining" existing chunks. We give libc for this challenge.

Committed four hours into CSAW RED. 

## TODO: Everything works, just need to test it on CTFd. 
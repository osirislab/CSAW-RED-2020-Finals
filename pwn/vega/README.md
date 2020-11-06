# Description

Use ROP to get past the multiple "Doom" gates and construct the flag along the way (Rick style).  

The player has to do a significant bit of reverse engineering for this challenge; the functions they have 
to jump to aren't accessible from `main`, so IDA Pro chokes when looking for functions although Ghidra does fine. 

The challenge is Doom themed because who doesnt love Doom. 

# TODO

Tested locally and on local Docker container by N4T_20. Needs to be tested on CTFd. 
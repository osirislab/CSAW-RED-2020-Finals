# Overview

This challenge utilizes a RSA blinding attack to forge the signature of a string that the server will not sign.

# Details

RSA encryption and signature verification involve computing x^e (mod n). RSA decryption and signature generation involve computing x^d (mod n). Since e and n are public (d is private), and (x^e)^d = x^(ed) = x^(de) = (x^d)^e (mod n), we can abuse this symmetry. We take our message m, create m' = m r^e (mod n), send m' for the server to sign, get m'^d = m^d r^(ed) = m^d r (mod n), and recover m^d via "division" modulo n. Finally, we retrieve the flag.

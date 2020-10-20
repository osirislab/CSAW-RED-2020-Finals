
# Leomund's secret flag

Here's the challenge design:
1. Server reads the flag, calculates its md5 hash, and creates a plaintext 
   comprised of "The password is Strahd and the flaghash is [md5sum]".
2. Server encrypts the plaintext and sends it to the user
3. Server asks the user for the encrypted new password
4. Server unencrypts the new text and checks the padding, then checks 
   that the new password is "Argenvost" and the flaghash is the same
5. To make the challenge harder, so that off-the-shelf padding oracle 
   busters can't solve it, we roll our own padding design. That forces
   people to understand how to really use a padding oracle.

Here's how to beat the challenge:
1. Figure out the padding
2. Decrypt a plaintext block one byte at a time by discarding any following
   plaintext blocks and modifying the previous ciphertext block, as per 
   standard padding oracle decryption. Get the flag hash that way
3. Without knowing the key, it's possible to encrypt by changing the 
   ciphertext in the block right before the ciphertext block that decrypts
   to known plaintext. Modifying that ciphertext block in turn changes what 
   its text would decrypt to, but we have a padding oracle to tell us the 
   new plaintext. So we start with the last block and work our way forward 
   until we have a full, new, encrypted plaintext message without ever having 
   known the key.

Credits:
"Magic Padding Oracle", PicoCTF 2018
https://nitish.ch/notes/writeup-of-a-few-picoctf-challenges/#magic-padding-oracle
Crypto101, Dan Boneh, Coursera
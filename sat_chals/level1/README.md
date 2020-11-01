# Out Of Contact

## TODO:
[] theming

## Premise

The communication period with your satellite will end in 3 minutes, but the flag won't print for another 6.  If only there were some way to buy more time...

## Solution

Edit the indexedDB entry containing `enctime`.  The current `enctime` is the end-of-contact time, XORed with the spacecraft id.  Both of these numbers are
available directly in indexedDB.  The solution is to decode the `enctime` timestamp, add time to it, reencode it, and enter it back into the database to send
it back. Then wait.

## Skills

IndexedDB, reading javascript.

## Flag

`flag{gr0und_c0ntr01_2_mJ0r_T0m_c0mmenc1nG_c0und0wn_3ngin3s_0n}`
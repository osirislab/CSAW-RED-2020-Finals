# cobol.gov

### Overview 

Cobol challenge. I rolled my own cobol http server. The way cobol does string parsing is super weird. If they take some time to read the cobol and try to understand the parsing they will spot a super simple parse bug that will let them read pretty much any path. A custom http request is required, so they'll need to connect with sockets and replicate the http request.


### Solution

They just need to send a request with a path like `A/flag.txt`. The cobol program will take out the A assuming its a leading forward slash. The cobol will then read whats left (flag.txt) and print it to screen. The actual http request will need to look something like:

```
AAA A/flag.txt AAA\r
\r
\r
```

The carriage return characters are importaint as the cobol program relies on them for parsing.

### Flag

flag{all_the_cool_kids_know_cobol}


### Files

They should be given the main.cobol file. Otherwise this program is shooting in the dark. The point is to understand the cobol.

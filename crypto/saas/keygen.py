from gmpy2 import invert, mpz, mul, powmod
import subprocess

def gen_prime():
	return int(subprocess.run("openssl prime -generate -bits 512".split(" "), capture_output = True).stdout.decode("utf-8")[:-1])

p = gen_prime()
q = gen_prime()
n = mul(p, q)

phi = mul(p - 1, q - 1)

#pub exponent
e = 65537
d = invert(e, phi)

with open("PUBLIC.py", "w") as file:
	file.write("n = " + str(n) + "\n")
	file.write("e = " + str(e))

with open("SECRET.py", "w") as file:
	file.write("d = " + str(d))

subprocess.call("vi -s auto_fill_pubkey.vim server.py".split(" "))
subprocess.call("vi -s auto_fill_pubkey.vim solver.py".split(" "))

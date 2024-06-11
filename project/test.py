import sys
import requests
import io

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

url = 'http://localhost:5000/upload'
file_path = 'C:/P/AnonDocService/test3.pdf'

with open(file_path, 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)

print(response.text)

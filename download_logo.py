import urllib.request
import os

url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Microsoft_Office_Excel_%282019%E2%80%93present%29.svg/256px-Microsoft_Office_Excel_%282019%E2%80%93present%29.svg.png'
target_path = os.path.join(os.getcwd(), 'excel_logo.png')

req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
    }
)

try:
    with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print(f"SUCCESS: Logo downloaded to {target_path}")
except Exception as e:
    print(f"ERROR: {e}")

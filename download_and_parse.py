
import os
import json
import pandas as pd
import subprocess
from netCDF4 import Dataset
import requests

# Config
CMEMS_USERNAME = os.getenv('CMEMS_USERNAME')
CMEMS_PASSWORD = os.getenv('CMEMS_PASSWORD')
GITHUB_REPO = os.getenv('GITHUB_REPO')  # format: username/repo
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def download_nc():
    print("🚀 Downloading .nc file...")
    cmd = [
        "python", "-m", "motuclient",
        "--motu", "https://nrt.cmems-du.eu/motu-web/Motu",
        "--service-id", "SERVICE_ID",
        "--product-id", "PRODUCT_ID",
        "--longitude-min", "104.0",
        "--longitude-max", "105.0",
        "--latitude-min", "0.8",
        "--latitude-max", "1.5",
        "--date-min", "2025-04-25 00:00:00",
        "--date-max", "2025-04-26 23:59:59",
        "--variable", "zos",
        "--out-dir", "./data",
        "--out-name", "sea_level.nc",
        "--user", CMEMS_USERNAME,
        "--password", CMEMS_PASSWORD
    ]
    subprocess.run(cmd, check=True)

def parse_nc_to_json():
    print("🔄 Parsing .nc to .json...")
    nc_file = "./data/sea_level.nc"
    output_json = "./data/sea_level.json"
    
    dataset = Dataset(nc_file)
    times = dataset.variables['time'][:]
    zos = dataset.variables['zos'][:]
    times = pd.to_datetime(times, unit='h', origin=pd.Timestamp('1950-01-01'))

    data = []
    for t, z in zip(times, zos):
        data.append({
            "time": t.strftime("%Y-%m-%d %H:%M:%S"),
            "zos": float(z)
        })

    with open(output_json, 'w') as f:
        json.dump(data, f, indent=4)

    print("✅ JSON file created!")

def upload_to_github():
    print("☁️ Uploading to GitHub...")
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/data/sea_level.json"
    
    with open("./data/sea_level.json", "r") as file:
        content = file.read()

    import base64
    content_base64 = base64.b64encode(content.encode()).decode()

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    r = requests.get(api_url, headers=headers)
    if r.status_code == 200:
        sha = r.json()["sha"]
        data = {
            "message": "update sea_level.json",
            "content": content_base64,
            "sha": sha
        }
        r = requests.put(api_url, headers=headers, json=data)
    else:
        data = {
            "message": "add sea_level.json",
            "content": content_base64
        }
        r = requests.put(api_url, headers=headers, json=data)

    if r.status_code in [200, 201]:
        print("✅ Upload berhasil!")
    else:
        print(f"❌ Upload gagal: {r.content}")

if __name__ == "__main__":
    os.makedirs("./data", exist_ok=True)
    download_nc()
    parse_nc_to_json()
    upload_to_github()

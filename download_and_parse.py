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
        "--service-id", "SEALEVEL_GLO_PHY_L4_MY_008_047-TDS",  # Service ID sesuai
        "--product-id", "dataset-duacs-rep-global-merged-allsat-phy-l4",  # Product ID sesuai
        "--longitude-min", "103.5",  # Longitude wilayah Batam
        "--longitude-max", "104.5",  # Longitude wilayah Batam
        "--latitude-min", "0.8",  # Latitude wilayah Batam
        "--latitude-max", "1.5",  # Latitude wilayah Batam
        "--date-min", "2025-04-25 00:00:00",
        "--date-max", "2025-04-26 23:59:59",
        "--variable", "adt",  # Menggunakan variabel 'adt' untuk tinggi permukaan laut
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
    adt = dataset.variables['adt'][:]  # Mengambil variabel 'adt' yang sesuai
    times = pd.to_datetime(times, unit='h', origin=pd.Timestamp('1950-01-01'))

    data = []
    for t, z in zip(times, adt):
        data.append({
            "time": t.strftime("%Y-%m-%d %H:%M:%S"),
            "adt": float(z)  # Menggunakan 'adt' untuk output
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

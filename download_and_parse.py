import os
import json
import pandas as pd
import subprocess
from netCDF4 import Dataset
from datetime import datetime

# Config
CMEMS_USERNAME = os.getenv('CMEMS_USERNAME')
CMEMS_PASSWORD = os.getenv('CMEMS_PASSWORD')

def download_nc():
    print("🚀 Downloading .nc file...")
    now = datetime.utcnow()
    date_min = now.strftime("%Y-%m-%d 00:00:00")
    date_max = now.strftime("%Y-%m-%d 23:59:59")
    cmd = [
        "python", "-m", "motuclient",
        "--motu", "https://nrt.cmems-du.eu/motu-web/Motu",
        "--service-id", "SEALEVEL_GLO_PHY_L4_MY_008_047-TDS",
        "--product-id", "dataset-duacs-rep-global-merged-allsat-phy-l4",
        "--longitude-min", "103.5",
        "--longitude-max", "104.5",
        "--latitude-min", "0.8",
        "--latitude-max", "1.5",
        "--date-min", date_min,
        "--date-max", date_max,
        "--variable", "adt",
        "--out-dir", "./data",
        "--out-name", "sea_level.nc",
        "--user", CMEMS_USERNAME,
        "--password", CMEMS_PASSWORD
    ]
    subprocess.run(cmd, check=True)
    print("✅ Download selesai!")

def parse_nc_to_json():
    print("🔄 Parsing .nc to .json...")
    nc_file = "./data/sea_level.nc"
    output_json = "./data/sea_level.json"

    if not os.path.exists(nc_file):
        raise FileNotFoundError(f"❌ File {nc_file} tidak ditemukan. Pastikan file sudah diunduh.")

    dataset = Dataset(nc_file)
    times = dataset.variables['time'][:]
    adt = dataset.variables['adt'][:]
    times = pd.to_datetime(times, unit='h', origin=pd.Timestamp('1950-01-01'))

    data = []
    for t, z in zip(times, adt):
        data.append({
            "time": t.strftime("%Y-%m-%d %H:%M:%S"),
            "adt": float(z)
        })

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=4)

    print("✅ JSON file created!")

if __name__ == "__main__":
    os.makedirs("./data", exist_ok=True)
    download_nc()
    parse_nc_to_json()

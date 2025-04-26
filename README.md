
# Pasang Surut Generator

## Deskripsi
Script ini:
- Download file `.nc` dari CMEMS
- Parsing ke `.json`
- Upload ke GitHub

## Setup Local
1. Install library:
   ```
   pip install -r requirements.txt
   ```
2. Buat file `.env` isikan:
   ```
   CMEMS_USERNAME=...
   CMEMS_PASSWORD=...
   GITHUB_REPO=...
   GITHUB_TOKEN=...
   ```

## Deploy ke Railway
- Upload project ini ke Railway
- Setting Environment Variables di Railway sesuai `.env.example`
- Tambahkan Scheduler (cronjob) di Railway

## Jadwal Scheduler Contoh
- Set cron di Railway ke:
  ```
  0 * * * *
  ```
  Artinya: jalan tiap 1 jam sekali.

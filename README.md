# Photo Transfer

Photo Transfer is a small Flask app for transferring photos from a phone to a computer over a local Wi-Fi network. Uploads are saved on the computer running the app; they are not sent to a cloud service.

## Features

- Create a transfer session and display a QR code for opening the phone upload page.
- Upload multiple photos from a phone and show accepted and rejected counts.
- Validate image format, file size, and image dimensions before saving.
- Expire the active session after 120 seconds.

## Technology

Python, Flask, Pillow, qrcode, HTML, CSS, and JavaScript.

## Project structure

```text
app.py                  Flask application entry point
config.py               Upload and session limits
routes/upload.py        Pages, QR code, and upload route
services/               Session and image handling
templates/              HTML templates
static/                 CSS and JavaScript
shared_photos/           Local destination for uploaded photos (created as needed)
requirements.txt         Python dependencies
```

## Requirements

- Python 3.9 or newer
- A computer and phone connected to the same Wi-Fi network

## Install and run

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`, then start the app with `.\.venv\Scripts\python.exe app.py`.

### Linux or macOS

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

The terminal prints the local address to use on the phone. Open it in a phone browser or scan the QR code shown on the computer, choose photos, and submit them. Uploaded files are stored in a timestamped folder under `shared_photos/`.

## Limits and security

- Up to 20 photos per request, 15 MB per file, and 100 MB per request.
- Accepted formats: JPEG, PNG, and WEBP.
- Only one active session is supported; starting a new session replaces the previous one. Each session lasts 120 seconds.
- The app is intended for a trusted local Wi-Fi network. It uses HTTP without HTTPS or authentication. Anyone with access to the local network and the active upload link may be able to submit files.
- Old photo folders are not removed automatically. Remove them manually when they are no longer needed.
- In the exceptional case of a write error followed by a failure to remove the partial file, an incomplete file may remain in the destination folder.


## Screenshots

### 1. Desktop - Active session and QR code

![Desktop view with QR code](photo/1.png)

### 2. Mobile - Photo upload

![Mobile upload page](photo/2.png)

### 3. Mobile - Upload completed

![Mobile upload confirmation](photo/3.png)

### 4. Desktop - Session expired

![Desktop session expired screen](photo/4.png)

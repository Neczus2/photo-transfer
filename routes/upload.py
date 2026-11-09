from io import BytesIO
import socket

import qrcode
from flask import render_template, request, send_file

from config import MAX_FILES, UPLOAD_FOLDER
from services import session
from services.image_handler import save_image, validate_image


def get_local_ip():
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        connection.connect(("8.8.8.8", 80))
        ip_address = connection.getsockname()[0]
    finally:
        connection.close()
    return ip_address


def home():
    token = session.create_session(UPLOAD_FOLDER)
    return render_template(
        "index.html",
        token=token,
        expiration_timestamp=session.get_session_expiration_timestamp(),
    )


def generate_qr():
    if not session.active_session_token:
        return "Brak aktywnej sesji", 404

    if not session.is_session_valid(session.active_session_token):
        return "Sesja wygasĹ‚a", 410

    address = f"http://{get_local_ip()}:5000/upload/{session.active_session_token}"
    qr_image = qrcode.make(address)
    image_buffer = BytesIO()
    qr_image.save(image_buffer, format="PNG")
    image_buffer.seek(0)
    return send_file(image_buffer, mimetype="image/png")


def upload(token):
    if not session.is_session_valid(token):
        return render_template("session_expired.html"), 403

    if request.method == "GET":
        return render_template(
            "index.html",
            token=session.active_session_token,
            mobile_upload=True,
            expiration_timestamp=session.get_session_expiration_timestamp(),
        )

    photos = request.files.getlist("photos")
    if not photos or all(not photo.filename for photo in photos):
        return render_template(
            "index.html",
            token=session.active_session_token,
            mobile_upload=True,
            expiration_timestamp=session.get_session_expiration_timestamp(),
            error_message="Nie wybrano żadnych zdjęć. Spróbuj ponownie.",
        ), 400

    if len(photos) > MAX_FILES:
        return render_template(
            "index.html",
            token=session.active_session_token,
            mobile_upload=True,
            expiration_timestamp=session.get_session_expiration_timestamp(),
            error_message=f"Możesz przesłać maksymalnie {MAX_FILES} zdjęć jednocześnie.",
        ), 400

    saved_count = 0
    rejected_count = 0
    save_error = False

    for photo in photos:
        if not photo.filename:
            continue

        if not validate_image(photo):
            rejected_count += 1
            continue

        valid_filename, file_saved = save_image(photo, session.active_transfer_folder)
        if not valid_filename:
            rejected_count += 1
            continue
        if not file_saved:
            save_error = True
            rejected_count += 1
            continue
        saved_count += 1

    error_message = (
        f"Nie udało się przesłać {rejected_count} plików. "
        f"Sprawdź ich format i rozmiar."
        if rejected_count > 0 else None
    )
    if save_error:
        save_message = "Nie udało się zapisać części zdjęć na dysku."
        error_message = f"{error_message or ''} {save_message}".strip()

    return render_template(
        "index.html",
        token=session.active_session_token,
        mobile_upload=True,
        saved_count=saved_count,
        rejected_count=rejected_count,
        expiration_timestamp=session.get_session_expiration_timestamp(),
        error_message=error_message,
    )


def file_too_large(error):
    return render_template(
        "index.html",
        token=session.active_session_token,
        mobile_upload=True,
        expiration_timestamp=session.get_session_expiration_timestamp(),
        error_message="Łączny rozmiar przesyłanych plików przekracza limit 100 MB. Wybierz mniej zdjęć.",
    ), 413


def register_routes(app):
    app.add_url_rule("/", endpoint="home", view_func=home, methods=["GET"])
    app.add_url_rule("/qr", endpoint="generate_qr", view_func=generate_qr, methods=["GET"])
    app.add_url_rule(
        "/upload/<token>", endpoint="upload", view_func=upload, methods=["GET", "POST"]
    )
    app.register_error_handler(413, file_too_large)

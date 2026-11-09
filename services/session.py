from datetime import datetime
import secrets

from config import SESSION_TIMEOUT


active_session_token = None
active_transfer_folder = None
active_session_last_activity = None


def create_session(upload_folder):
    global active_session_token, active_transfer_folder, active_session_last_activity

    active_session_token = secrets.token_urlsafe(16)
    active_session_last_activity = datetime.now()
    transfer_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    active_transfer_folder = upload_folder / transfer_id
    return active_session_token


def get_session_expiration_timestamp():
    if not active_session_last_activity:
        return None

    expiration_time = active_session_last_activity + SESSION_TIMEOUT
    return expiration_time.timestamp()


def is_session_valid(token):
    if not active_session_token or not active_session_last_activity:
        return False

    if not secrets.compare_digest(token, active_session_token):
        return False

    if datetime.now() - active_session_last_activity > SESSION_TIMEOUT:
        return False

    return True

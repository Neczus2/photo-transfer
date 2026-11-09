import warnings
from uuid import uuid4

from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from config import (
    ALLOWED_FORMATS,
    MAX_FILE_SIZE,
    MAX_IMAGE_DIMENSION,
    MAX_IMAGE_PIXELS,
)


def validate_image(photo):
    try:
        photo.stream.seek(0, 2)
        file_size = photo.stream.tell()
        photo.stream.seek(0)

        if file_size > MAX_FILE_SIZE or file_size == 0:
            return False

        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(photo.stream) as image:
                if image.format not in ALLOWED_FORMATS:
                    return False

                width, height = image.size
                if (
                    width > MAX_IMAGE_DIMENSION
                    or height > MAX_IMAGE_DIMENSION
                    or width * height > MAX_IMAGE_PIXELS
                ):
                    return False

                image.verify()
        photo.stream.seek(0)

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        ValueError,
    ):
        return False

    return True


def save_image(photo, transfer_folder):
    filename = secure_filename(photo.filename)
    if not filename:
        return False, False

    try:
        transfer_folder.mkdir(parents=True, exist_ok=True)
        file_saved = False

        for _ in range(5):
            candidate_filename = f"{uuid4().hex[:16]}_{filename}"
            destination = transfer_folder / candidate_filename
            created = False

            try:
                with destination.open("xb") as output_file:
                    created = True
                    photo.stream.seek(0)
                    photo.save(output_file)
                file_saved = True
                break
            except FileExistsError:
                continue
            except OSError:
                if created:
                    destination.unlink(missing_ok=True)
                raise

        return True, file_saved
    except OSError:
        return True, False

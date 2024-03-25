import os
import secrets

from flask import current_app

from PIL import Image


def save_profile_picture(form_profile_picture):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_profile_picture.filename)
    profile_picture_file_name = random_hex + file_extension
    profile_picture_path = os.path.join(current_app.root_path, "static/images/uploads/", profile_picture_file_name)
    profile_picture_output_size = (1080, 1080)
    profile_picture = Image.open(form_profile_picture)
    profile_picture.thumbnail(profile_picture_output_size)
    profile_picture.save(profile_picture_path)
    return profile_picture_file_name

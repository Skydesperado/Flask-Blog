import os
import secrets

from flask import current_app

from PIL import Image


def save_post_picture(form_post_picture):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_post_picture.filename)
    post_picture_file_name = random_hex + file_extension
    post_picture_path = os.path.join(current_app.root_path, "static/images/uploads/", post_picture_file_name)
    post_picture_output_size = (1080, 1080)
    post_picture = Image.open(form_post_picture)
    post_picture.thumbnail(post_picture_output_size)
    post_picture.save(post_picture_path)
    return post_picture_file_name

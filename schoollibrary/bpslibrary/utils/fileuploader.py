import os
from flask import request
from werkzeug.utils import secure_filename
from bpslibrary.utils.enums import FileType


def upload_to_tmp(post_request: request, file_name: str, file_type: FileType):
    """Upload a file to tmp and return its path."""
    if file_type == FileType.IMAGE:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']

    if file_type == FileType.CSV:
        allowed_extensions = ['csv']

    if file_name not in post_request.files:
        raise FileNotFoundError("Could not find the file!")

    file = post_request.files[file_name]

    if file.filename == '':
        raise ValueError("No files have been selected.")

    if '.' not in file.filename or \
       file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        raise ValueError("This file type is not permitted.")

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('/tmp', filename)
        file.save(file_path)

    return file_path

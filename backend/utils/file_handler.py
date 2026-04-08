import os
import uuid


class FileHandler:

    @staticmethod
    def save_file(file, folder="uploads/documents", allowed_types=None):
        """
        Save uploaded file safely

        :param file: UploadFile
        :param folder: target folder
        :param allowed_types: list of allowed MIME types
        :return: file path
        """

        # 🔹 Validate type
        if allowed_types and file.content_type not in allowed_types:
            raise ValueError("Invalid file type")

        # 🔹 Ensure folder exists
        if not os.path.exists(folder):
            os.makedirs(folder)

        # 🔹 Generate unique filename
        extension = file.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{extension}"

        file_path = os.path.join(folder, unique_name)

        # 🔹 Save file
        try:
            with open(file_path, "wb") as f:
                f.write(file.file.read())
        except Exception as e:
            raise RuntimeError("File upload failed")

        return file_path

    @staticmethod
    def delete_file(file_path):
        """
        Delete file safely
        """
        if os.path.exists(file_path):
            os.remove(file_path)
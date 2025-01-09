import os
from werkzeug.utils import secure_filename
import uuid


def save_file(file, upload_folder="app/static/files"):
    """
    Сохраняет файл в указанной директории и возвращает оригинальное и новое название файла, а также путь.

    :param file: Объект файла, переданный из формы.
    :param upload_folder: Папка, куда будет сохранен файл.
    :return: Словарь с оригинальным названием файла, новым названием и путём.
    """
    # Убедимся, что папка существует
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Оригинальное название файла
    original_filename = secure_filename(file.filename)

    # Генерация уникального имени файла
    new_filename = f"{uuid.uuid4().hex}_{original_filename}"

    # Полный путь сохраненного файла
    file_path = os.path.join(upload_folder, new_filename)

    # Сохраняем файл
    file.save(file_path)

    return {
        "original_filename": original_filename,
        "new_filename": new_filename,
        "file_path": file_path
    }

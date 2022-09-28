import shutil
import sys
from pathlib import Path

from . import file_parser as parser
from .normalize import normalize


def handle_media(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))


def handle_other(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))


def handle_archive(filename: Path, target_folder: Path) -> None:
    # Создаем папку для архивов
    target_folder.mkdir(exist_ok=True, parents=True)
    # Создаем папку куда распаковываем архив
    # берем суффикс у файла и убираем replace(filename.suffix, '')
    folder_for_file = target_folder / \
        normalize(filename.name.replace(filename.suffix, ''))
    #  создаем папку для архива с именем файла

    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()),
                              str(folder_for_file.resolve()))
    except shutil.ReadError:
        print(f"{filename} isn't an archive!")
        folder_for_file.rmdir()
        return None
    filename.unlink()


def handle_folder(folder: Path) -> None:
    try:
        folder.rmdir()
    except OSError:
        print(f'Not possible to delete folder {folder}')


def main(folder: Path) -> None:
    parser.scan(folder)

    for file in parser.IMAGES:
        handle_media(file, folder / 'images')
    for file in parser.DOCUMENTS:
        handle_media(file, folder / 'documents')
    for file in parser.AUDIO:
        handle_media(file, folder / 'audio')
    for file in parser.VIDEO:
        handle_media(file, folder / 'video')

    for file in parser.ARCHIVES:
        handle_archive(file, folder / 'archives')

    for file in parser.OTHER:
        handle_other(file, folder / 'OTHER_TYPES')

    # Выполняем реверс списка для того, чтобы все папки удалить.
    # we don't need to anything with files of OTHER type => exclude folders that contain them
    for folder in parser.FOLDERS[::-1]:
        handle_folder(folder)


def start():
    if sys.argv[1]:
        scan_folder = Path(sys.argv[1])
        print(f'Start in folder {scan_folder.resolve()}')
        main(scan_folder.resolve())


# This decorator handles the correct number of arguments that are passed into the function
def func_arg_error(func):
    def wrapper(*args):
        try:
            result = func(*args)
            return result
        except TypeError:
            f_name = func.__name__
            if f_name in ('sort_folder',):
                return "ERROR: This command has to be written with 1 argument!"
            return "Some unhandled error occurred!"
    return wrapper


@func_arg_error
def sort_folder(folder: str) -> str:
    path = Path(folder)
    if not path.exists():
        return f"This folder ({folder}) does not exist!"

    scan_folder = path
    print(f'Start in folder {scan_folder.resolve()}')
    main(scan_folder.resolve())
    return f"Folder {folder} has been sorted!"


if __name__ == '__main__':
    if sys.argv[1]:
        folder_for_scan = Path(sys.argv[1])
        print(f'Start in folder {folder_for_scan.resolve()}')
        main(folder_for_scan.resolve())

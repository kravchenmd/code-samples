from datetime import datetime

from config.config import BASE_DIR
from pathlib import Path


def move_picture(user_subfolder: str, file_path: Path) -> tuple[str, int]:
    """
    Move, rename picture after uploading.
    Return relative path to the file and size for storing in the DB
    """
    target_folder = Path(BASE_DIR / "src" / "static" / user_subfolder)
    target_folder.mkdir(exist_ok=True)
    # add time stamp in filename (to exclude duplicated names)
    file = file_path.rename(target_folder / Path(str(datetime.now().strftime("%I_%M_%S")) + file_path.name))
    size = file.stat().st_size
    file_name_for_db = f"/static/{user_subfolder}/{file.name}"  # relative to `static` path for the DB
    return file_name_for_db, size


def delete_user_pic(file_path: str) -> None:
    filename = Path(f"{BASE_DIR}/src{file_path}")
    try:
        filename.unlink()
    except FileNotFoundError:
        raise

import asyncio
from pathlib import Path
# from queue import Queue, Empty
# from threading import Thread, Event
from time import time

from aiopath import AsyncPath

THREAD_POOL_SIZE = 4

# containers for file names
IMAGES = asyncio.Queue()
DOCUMENTS = asyncio.Queue()
AUDIO = asyncio.Queue()
VIDEO = asyncio.Queue()
ARCHIVES = asyncio.Queue()
OTHER = asyncio.Queue()

# set of folders for sorting
FOLDER_NAMES = ('archives', 'video', 'audio',
                'documents', 'images', 'OTHER_TYPES')

# dict to choose proper container based on the type of file
EXTENSIONS_CONT = {
    'images': IMAGES,
    'documents': DOCUMENTS,
    'audio': AUDIO,
    'video': VIDEO,
    'archives': ARCHIVES,
    'OTHER_TYPES': OTHER
}

# dict with types of files and known extensions
EXTENSIONS_DICT = {
    'images': ('jpg', 'jpeg', 'png', 'svg'),
    'documents': ('txt', 'doc', 'docx', 'pdf'),
    'audio': ('mp3', 'wav', 'wma'),
    'video': ('mp4', 'avi', 'mkv', 'mov'),
    'archives': ('zip', 'tar', 'gztar')
}

FOLDERS = []
EXTENSIONS = set()
UNKNOWN = set()
FOLDERS_UNKNOWN = []


async def get_extension(filename: str) -> str:
    return AsyncPath(filename).suffix[1:].lower()  # just changed to lower()


def find_sub_folders(folder: Path, folder_queue_: asyncio.Queue) -> None:
    """
    Finds all sub-folders of the folder and adds them to the list FOLDERS.
    """
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in FOLDER_NAMES:
                FOLDERS.append(item)
                folder_queue_.put_nowait(item)
                find_sub_folders(item, folder_queue_)


async def scan_folders(folder_queue_async_: asyncio.Queue, event_: asyncio.Event) -> None:  # , event: Event
    """
    Scans the folder and fill containers with files names sorted by their type,
    names of folders and extensions.
    """
    # print("Start working")
    while not folder_queue_async_.empty():
        try:
            folder = AsyncPath(await folder_queue_async_.get())  # block=False
        except asyncio.QueueEmpty:
            break
        else:
            for item in Path(folder).iterdir():
                if item.is_file():
                    ext = await get_extension(item.name)  # взять расширение
                    fullname = folder / item.name  # взять полный путь к файлу
                    if not ext:  # если у файла нет расширения добавить к неизвестным
                        await OTHER.put(fullname)
                    else:
                        for k, v in EXTENSIONS_DICT.items():
                            # at first choose type of extension
                            if ext in v:
                                # then choose proper container
                                container: asyncio.Queue = EXTENSIONS_CONT[k]
                                EXTENSIONS.add(ext)
                                await container.put(fullname)
                                break
                        else:
                            # Если мы не регистрировали расширение в REGISTER_EXTENSIONS, то добавить в другое
                            UNKNOWN.add(ext)
                            await OTHER.put(fullname)
                            # save folder that contain file with type OTHER
                            FOLDERS_UNKNOWN.append(item.parent.absolute())
            # folder_queue_async_.task_done()
    event_.set()
    # print("Finished")
    # print(f'Images: {IMAGES.qsize()}')
    # print(f'Documents: {DOCUMENTS.qsize()}')
    # print(f'Audio: {AUDIO.qsize()}')
    # print(f'Video: {VIDEO.qsize()}')
    # print(f'Archives: {ARCHIVES.qsize()}')
    # print(f'OTHER: {OTHER.qsize()}')


async def main():
    # folder_for_scan = Path(sys.argv[1])
    folder_for_scan = AsyncPath("testapp")
    print(f'Scanning folder {folder_for_scan}')

    folder_queue_async = asyncio.Queue()
    folder_queue_async.put_nowait(folder_for_scan)
    find_sub_folders(Path(folder_for_scan), folder_queue_async)
    print(f'Found {folder_queue_async.qsize()}')
    # print(f'Folders: {list(folder_queue_async._queue)[:5]}')

    start = time()
    event = asyncio.Event()

    # await scan_folders(folder_queue_async, event)
    # await folder_queue_async.join()

    producers = [asyncio.create_task(scan_folders(folder_queue_async, event)) for _ in range(3)]

    await asyncio.gather(*producers)
    await folder_queue_async.join()

    print(f"Execution time: {time() - start}")
    print(f'Images: {IMAGES.qsize()}')
    print(f'Documents: {DOCUMENTS.qsize()}')
    print(f'Audio: {AUDIO.qsize()}')
    print(f'Video: {VIDEO.qsize()}')
    print(f'Archives: {ARCHIVES.qsize()}')
    print(f'OTHER: {OTHER.qsize()}')


if __name__ == '__main__':
    asyncio.run(main())

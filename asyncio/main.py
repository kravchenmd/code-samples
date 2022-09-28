import asyncio
import os
import shutil
# import sys
from pathlib import Path
from time import time, process_time

from aiofiles.os import wrap
from aiopath import AsyncPath

import file_parser as parser
from normalize import normalize

copyfile = wrap(shutil.copy2)


async def replace_file(file: AsyncPath, target_path: AsyncPath) -> None:
    await copyfile(file, target_path)


def archive_unpack(filename: Path, target_folder: Path):
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()),
                              str(folder_for_file.resolve()))
    except shutil.ReadError:
        print(f"{filename} isn't an archive!")
        folder_for_file.rmdir()


async def async_archive_upack(filename: Path, target_folder: Path):
    return await asyncio.to_thread(archive_unpack, filename, target_folder)


async def handle_file(filename: AsyncPath, target_folder: AsyncPath, file_type: str):
    # print("Handler: started")
    # await asyncio.sleep(0.1)
    target_folder = target_folder / file_type
    await target_folder.mkdir(exist_ok=True, parents=True)
    if file_type != 'archives':
        normalized_name = normalize(filename.name)
        # await filename.replace(AsyncPath(target_folder) / normalized_name)  # + move `unlink' to the else-part
        await replace_file(filename, target_folder / normalized_name)
    else:
        await async_archive_upack(Path(filename), Path(target_folder))
    await filename.unlink()  # tab this `unlink` inside `else` to use `replace`
    # print("Handler: finished")


def handle_folder(folder_: Path) -> None:
    try:
        folder_.rmdir()
    except OSError:
        print(f'Not possible to delete folder {folder_}')


async def worker_media(folder_: AsyncPath, event_: asyncio.Event):  # , event_: Event, lock_: RLock
    # print("Worker: started")
    empty = False
    while not (event_.is_set() and empty):
        empty = True
        for key, work_queue in parser.EXTENSIONS_CONT.items():
            if not work_queue.empty():
                file = await work_queue.get()
                # print(f"File {file}")
                await handle_file(file, folder_, key)
                empty = False
                work_queue.task_done()
        if event_.is_set() and empty:
            # print("Worker: stopped")
            break


def prepare_folder(target_folder: Path, source_folder: Path):
    """
    Clean folder `testapp` (if exist) and copy all content from folder `garbage`
    """
    print("Prepare folder")
    if target_folder.exists():
        shutil.rmtree(target_folder)
    shutil.copytree(source_folder, target_folder)

    file_count = sum(len(files) for _, _, files in os.walk(target_folder))
    print(f"Number of files in the folder before sorting: {file_count}")


def sanitize_folder(sort_folder: Path, start_time_: float, start_time_cpu_: float):
    """
    Delete rest folders after sorting
    """
    # Выполняем реверс списка для того, чтобы все папки удалить.
    # we don't need to anything with files of OTHER type => exclude folders that contain them
    print("Sanitize")
    for folder_ in parser.FOLDERS[::-1]:
        handle_folder(folder_)

    print(f"Execution time (wall): {round((time() - start_time_) * 1000)} ms")
    print(f"Execution time (CPU): {round((process_time() - start_time_cpu_) * 1000)} ms")

    file_count = sum(len(files) for _, _, files in os.walk(sort_folder))
    print("Sorting is finished!")
    print(f"Number of files in the folder after sorting: {file_count}\n")


async def start_sync(folder_queue_async_: asyncio.Queue, sort_folder_: AsyncPath, event_: asyncio.Event):
    """
    Sorting without Threads
    """
    print(f"Start sync sorting ")
    start_time, start_time_cpu = time(), process_time()
    await parser.scan_folders(folder_queue_async_, event_)
    await worker_media(sort_folder_, event_)

    # delete remaining empty folders
    sanitize_folder(sort_folder_, start_time, start_time_cpu)


async def start_async(folder_queue_async_: asyncio.Queue, sort_folder_: AsyncPath, event_: asyncio.Event):
    """
        Sorting using Threads
        """
    print(f"Start async sorting ")
    start_time, start_time_cpu = time(), process_time()

    scanners = [asyncio.create_task(parser.scan_folders(folder_queue_async_, event_)) for _ in range(2)]

    copiers = [asyncio.create_task(worker_media(sort_folder_, event_)) for _ in range(5)]

    await asyncio.gather(*scanners)
    # await folder_queue_async_.join()
    [await el.join() for el in parser.EXTENSIONS_CONT.values()]
    for copier in copiers:
        copier.cancel()

    # delete remaining empty folders
    sanitize_folder(sort_folder_, start_time, start_time_cpu)


async def main():
    # if sys.argv[1]:
    #     sort_path = sys.argv[1]
    #     print(f'Start in folder {sort_path.resolve()}')
    # else:
    sort_path = "testapp"
    garbage_path = "garbage"

    sort_folder = AsyncPath(sort_path)

    print("SORTING SYNC")
    prepare_folder(Path(sort_path), Path(garbage_path))  # Path(sort_path)

    folder_queue_async = asyncio.Queue()
    folder_queue_async.put_nowait(sort_folder)
    parser.find_sub_folders(Path(sort_folder), folder_queue_async)
    print(f'Found {folder_queue_async.qsize()}')

    event = asyncio.Event()
    await start_sync(folder_queue_async, sort_folder, event)

    parser.FOLDERS = []
    print("SORTING ASYNC")
    prepare_folder(Path(sort_path), Path(garbage_path))
    folder_queue_async = asyncio.Queue()
    folder_queue_async.put_nowait(sort_folder)

    parser.find_sub_folders(Path(sort_folder), folder_queue_async)
    print(f'Found {folder_queue_async.qsize()}')

    event = asyncio.Event()
    await start_async(folder_queue_async, sort_folder, event)


if __name__ == '__main__':
    asyncio.run(main())

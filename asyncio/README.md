# Folder sorter (async)

## Description

**Project is implemented in the following way**:

1. At the beginning script finds folders and nested subfolders for further scanning of files to be sorted
2. Then the asynchronous scanning process of all folders is started: containers for corresponding type of file are
   filled (`asyncio.Queue` with `AsyncPath` elements). The process is going in tasks `scanners`
3. In parallel the process of moving is started: when one of the containers fills with a file it (file) submits for
   further moving to the corresponding directory
4. Sorting is finished when all containers become empty (`Event` flag signals that scanning is finished)

**In the script sorting goes 2 times**:

* 1st time "synchronously" (in fact, just with 2 tasks: one for scanning and one for copying)
* 2nd tyme asynchronously: 2 pools of tasks are created (`scanners` and `copiers`), their start happens on
  the `producer-consumer` model

* Asynchronous unpacking of archives is implemented by wrapping a synchronous function (using `shutil.unpack_archive`)
  in `asyncio.to_thread()`

## Results

There is visible increasing of the sorting process with using `copyfile = wrap(shutil.copy2)` as a copy function (bellow
are results for a folder with ~2000 files, ~25 MB in size, including one archive):

* "synchronous" sorting: **2693 ms**
* asynchronous version (2 scanners and 5 copiers); **1850 ms**

**_Kravchenko Michail_**

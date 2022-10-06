import os
import json
import hashlib

# Get All Files in provided directory and its subdirectories
def GetFilesRecursive(dirName, extension) -> list[str] :
    # List of dir and files
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # for each dir or file
    for entry in listOfFile:
        # get new location
        fullPath = os.path.join(dirName, entry)
        # Recursion on dirs
        if os.path.isdir(fullPath): 
            allFiles = allFiles + GetFilesRecursive(fullPath, extension)
        # append in file list
        elif fullPath.endswith(extension): 
            allFiles.append(fullPath)  
    return allFiles # Return list of files

# Get All Files in provided directory
def GetFiles(dirName, extension) -> list[str] :
    # List of dir and files
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # for each dir or file
    for entry in listOfFile:
        # get new location
        fullPath = os.path.join(dirName, entry)
        # check if it is a file
        if not os.path.isdir(fullPath) and fullPath.endswith(extension):
            allFiles.append(fullPath)  

    return allFiles # Return list of files

# Check Directories [Make If Not Present]
def ResolveDirectory(path: str) :
    if not path.endswith('/') :
        path += '/'

    length = path.__len__()
    current_dir = ""
    current_path = ""

    for index in range(length) :    
        value = path[index]
        current_dir += value
        
        if value == '/' :
            current_path += current_dir
            work_path = current_path[:current_path.__len__()-1]

            if not os.path.exists(work_path) :
                os.system(f'mkdir {work_path}')
            current_dir = ""


def ReadJSON(path) -> dict :
    if not os.path.exists(path) :
        return {}

    reader = open(path, 'r')
    content = reader.read()
    reader.close()

    return json.loads(content)

def GetHash(value) :
    value_bytes = bytes(value, 'utf-8')
    sha256Hash = hashlib.sha256(value_bytes).hexdigest()
    md5Hash = hashlib.md5(value_bytes).hexdigest()
    return sha256Hash + md5Hash


INCLUDE_PARAMS = [
    '#include <', '>',
    '#include<', '>',
    '#include"', '"',
    '#include "', '"'
]
def GetIncludes(path) -> list :
    includes = []

    reader = open(path, 'r')
    print(path)
    contentLines = reader.readlines()
    reader.close()
    
    multi_line_comment = False
    for line in contentLines :

        for i in range(4) :
            include_index = line.find(INCLUDE_PARAMS[i * 2])
            if include_index != -1 :
                break

        if include_index == -1 : 
            continue

        multi_line_comment = '/*' in line
        multi_line_comment = multi_line_comment and '*/' in line
        single_line_comment_index = line.find('//')

        if multi_line_comment :
            continue
        if single_line_comment_index != -1 and single_line_comment_index < include_index : 
            continue

        include_begin_index = include_index + len(INCLUDE_PARAMS[i * 2])
        include_end_index = include_begin_index + line[include_begin_index:].find(INCLUDE_PARAMS[i * 2 + 1])
        include = line[include_begin_index : include_end_index]
        includes.append(include)

    return includes
        
def CompareContent(path1: str, path2: str) -> bool :
    file1 = open(path1, 'r')
    file2 = open(path2, 'r')

    content1 = file1.read()
    content2 = file2.read()

    file1.close()
    file2.close()
    
    size1 = len(content1)
    size2 = len(content2)
    if size1 != size2 :
        return False

    for i in range(size1) :
        if content1[i] != content2[i] :
            return False

    return True
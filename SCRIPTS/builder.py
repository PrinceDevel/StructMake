from datatypes import *
from parser import *
from utils import *

import os
import json
CWD = os.getcwd()

def BuildWorkspace (workspace: Workspace) -> None :
    ResolveDirectory(workspace.statedir)

    for key in workspace.projects.keys() :
        project = workspace.projects[key]
        
        linkprj = project.linkprj
        project.linkprj = []
        
        for prj in linkprj :
            project.linkprj.append(workspace.projects[prj])

        BuildProject(project, workspace.statedir)

    if len(workspace.startup) != 0 :
        os.system(workspace.projects[workspace.startup].output)

def BuildProject (project: Project, statedir: str) -> None :
    statedir = statedir + project.name + '/'

    # Checking Existence of Directories
    ResolveDirectory(project.targetdir)
    ResolveDirectory(project.objdir)
    ResolveDirectory(statedir)

    # Checking Existence of State Directory
    StateFile = statedir + project.name + '.json'
    OldStates: dict = ReadJSON(StateFile)
    NewStates: dict = {}
    ChangeStates: dict = {}

    # ----- Flags for compiling lib -----
    objfileFlags = ""
    includeFlags = ""
    linklibFlags = ""
    linkdirFlags = ""
    defineFlags = ""
    ldlibsFlags = ""

    # Setting Up Include Dirs
    for directory in project.includedirs : 
        includeFlags += f'-I{directory} '

    # Setting Up Defines
    for key in project.defines.keys() :
        value = project.defines[key]

        if value == None :
            defineFlags += f'-D{key} '
        else :
            defineFlags += f'-D{key}={value} '
    
    # Setting Links to other projects
    for prj in project.linkprj :
        
        if prj.kind == 'static' :
            linklibFlags += f'-l{prj.name} '
            
            if prj.targetdir.endswith('/') :
                link = f'-L{prj.targetdir[:len(prj.targetdir)-1]} '
            else :
                link = f'-L{prj.targetdir} '
            
            if link not in linkdirFlags :
                linkdirFlags += link

        elif prj.kind == 'shared' :
            linklibFlags += f'-l{prj.name} '
            ldlibsFlags += f'{CWD}/{prj.targetdir}:'

    # Setting Link Libs [Library]
    for link in project.linkdirs :
        if link not in linkdirFlags :
            linkdirFlags += f'-L{link} '

    # Setting Link Dirs [Library]
    for link in project.linklibs :
        linklibFlags += f'-l{link} '

    # Setting Files To Be Resolved
    objfilePaths = []
    for path in project.files :
        starpos = path.rfind('*');

        if starpos != -1 :
            recursive = path[starpos -1] == '*'
            extension = path[starpos +1:]

            if recursive :
                subfilePaths = GetFilesRecursive(path[:starpos -2], extension)
            else :
                subfilePaths = GetFiles(path[:starpos -2], extension)

            for subPath in subfilePaths :
                if os.path.exists(subPath) :
                    objfilePaths.append(subPath)
                else :
                    print(f'File {subPath} does not exist ........')
        else :
            if os.path.exists(path) :
                objfilePaths.append(path)
            else :
                print(f'File {path} does not exist ........')

    # Resolving Files State
    for path in objfilePaths :
        ResolveFileState (
            path = path,
            OldStates = OldStates,
            NewStates = NewStates,
            ChangeStates = ChangeStates,
            includedirs = project.includedirs,
            statedir = statedir
        )

    # Resolving Files
    for path in objfilePaths :
        objpath = CompileObject(
            path = path,
            NewStates = NewStates,
            ChangeStates = ChangeStates,
            objdir = project.objdir,
            defineFlags = defineFlags,
            includeFlags = includeFlags,
            intFlags = project.intflags
        )
        if len(objpath) != 0 :
            objfileFlags += objpath

    # ------ Creating Static Library ------
    if project.kind == 'static' :

        project.output = f'{project.targetdir}lib{project.name}.a'
        os.system('echo -----------------------------------------')
        os.system(f'echo Building Static Library {project.name}...')
        os.system(f'ar rcs {project.outflags} {project.output} {objfileFlags} {linkdirFlags} {linklibFlags}')
        os.system(f'echo Built Static Library: {project.output}')
        os.system('echo -----------------------------------------')

    # ------ Creating Shared Library ------
    elif project.kind == 'shared' :
        
        project.output = f'{project.targetdir}lib{project.name}.so'
        os.system('echo -----------------------------------------')
        os.system(f'echo Building Shared Library {project.name}...')
        os.system(f'g++ -shared {project.outflags} -o {project.output} {objfileFlags} {linkdirFlags} {linklibFlags}')
        os.system(f'echo Built Shared Library: {project.output}')
        os.system('echo -----------------------------------------')

    # ------ Creating Executable ------
    elif project.kind == 'exec' :

        project.output = f'{project.targetdir}{project.name}'
        os.system('echo -----------------------------------------')
        os.system(f'echo Building Executable {project.name}...')
        os.system(f'g++ {project.outflags} -o {project.output} {objfileFlags} {linkdirFlags} {linklibFlags}')
        os.system(f'echo Build Executable: {project.output}')
        os.system('echo -----------------------------------------')

    # ------ Project Kind Not Defined ------
    else :
        os.system('echo --------- Project Kind Undefined ---------')


    project.LD_LIBS += ldlibsFlags
    
    content = json.dumps(NewStates, indent = 4)
    with open(StateFile, 'w') as writer :
        writer.write(content)

    for key in NewStates :
        with open(NewStates[key][0],'r') as reader, open(statedir + key,'w') as writer:
            writer.write(reader.read())    

def ResolveFileState (
    path: str,
    OldStates: dict,
    NewStates: dict,
    ChangeStates: dict,
    includedirs: list,
    statedir: str
) :
    if not os.path.exists(path) :
        return

    includes = ResolveIncludes(path, includedirs)
    key = path.replace('/', '_')
    
    modified = True
    if key in OldStates.keys() :
        modified = not CompareContent(path, statedir + key)

    ChangeStates[key] = [modified, '-1']
    if len(includes) == 0 :
        ChangeStates[key][1] = '0'

    NewStates[key] = [path]
    for include in includes :
        NewStates[key].append(include.replace('/', '_'))

def ResolveIncludes (path, includedirs) -> list[str] :
    unres_includes = GetIncludes(path)
    slash_index = path.rfind('/')

    includes = []
    directory = path[:slash_index + 1]

    for include in unres_includes :
        if os.path.exists(directory + include) :
            includes.append(directory + include)
            continue

        for includedir in includedirs :
            if not includedir.endswith('/') :
                includedir += '/'

            if os.path.exists(includedir + include) :
                includes.append(includedir + include)
                break

    return includes

def CompileObject(
    path: str,
    NewStates: dict,
    ChangeStates: dict,
    objdir: str,
    defineFlags = "",
    includeFlags = "",
    intFlags = ""    
) -> str :
    dot_index = path.rfind('.')
    
    extension = path[dot_index:]
    name = path[:dot_index].replace('/', '_')
    key = path.replace('/', '_')
    objpath = objdir + name + '.o '
    
    if not (extension == '.c' or extension == '.cpp') :
        objpath = "" 

    if not key in NewStates.keys() :
        return ""

    modified = IsFileModified(key, NewStates, ChangeStates)
    if not modified :
        return objpath

    if extension == '.c' :
        os.system(f'gcc {intFlags} {includeFlags} {defineFlags} -c {path} -o {objpath}')
        os.system(f'echo Created OBJ {objpath}')
        return objpath

    if extension == '.cpp' :
        os.system(f'g++ {intFlags} {includeFlags} {defineFlags} -c {path} -o {objpath}')
        os.system(f'echo Created OBJ {objpath}')
        return objpath

    return ""  

def IsFileModified (key, NewStates, ChangeStates) -> bool :
    if ChangeStates[key][0] or ChangeStates[key][1] == '1' :
        return True
    
    elif ChangeStates[key][1] == '0' : 
        return False

    count = len(NewStates[key])
    for i in range(1, count) :
        
        if NewStates[key][i] not in ChangeStates.keys() :
           continue

        modified = IsFileModified( NewStates[key][i], NewStates, ChangeStates )  
        if modified :
            ChangeStates[key][1] = '1'
            return True
    
    ChangeStates[key][1] = '0'
    return False








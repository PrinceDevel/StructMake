import yaml
from yaml.loader import SafeLoader
from datatypes import *

def ErrorExit(message: str = "") :
    print('ERROR:', message)
    exit()

def LoadYAML (path: str) -> any :
    with open (path, 'r') as reader :
        data = yaml.load(reader, Loader = SafeLoader)
    return data

def ParseYAML (structure: dict) -> Workspace :

    #######################################################
    ##################### WORKSPACE #######################
    #######################################################
    if 'workspace' not in structure.keys() :
        ErrorExit('No workspace found')
    workspaceS = structure['workspace']
    workspace = Workspace()

    #################### ESSENTIALS ########################
    if 'name' not in workspaceS.keys() :
        ErrorExit('[name] key not in workspace')
    workspace.name = workspaceS['name']

    if 'startup' not in workspaceS.keys() :
        ErrorExit('[startup] key not in workspace')
    workspace.startup = workspaceS['startup']

    if 'statedir' not in workspaceS.keys() :
        ErrorExit('[statedir] key not in workspace')
    workspace.statedir = workspaceS['statedir']

    #################### NON ESSENTIALS ########################
    if 'location' in workspaceS.keys() and workspaceS['location'] != None :
        workspace.location = workspaceS['location']
        


    #######################################################
    ##################### PROJECTS ########################
    #######################################################
    projectsS = []
    if 'projects' in structure.keys() :
        projectsS += structure['projects']
    
    ############### INCLUDED PROJECTS #####################
    if 'includes' in structure.keys() :
        includes = structure['includes']
        for include in includes :

            if not include.endswith('.yaml') :
                if not include.endswith('/') :
                    include += '/'
                include += 'struct.yaml'

            project:dict = LoadYAML(include)['project']
            projectsS.append(project)


    if len(projectsS) == 0 :
        ErrorExit('No Projects Found')
    projects:dict = {}

    for projectS in projectsS :
        project = Project()

        #################### ESSENTIALS ########################
        if 'name' not in projectS.keys() :
            ErrorExit('[name] key not in project')
        project.name = projectS['name']

        if 'kind' not in projectS.keys() :
            ErrorExit('[kind] key not in project')
        project.kind = projectS['kind']

        if 'targetdir' not in projectS.keys() :
            ErrorExit('[targetdir] key not in project')
        project.targetdir = projectS['targetdir']

        if 'objdir' not in projectS.keys() :
            ErrorExit('[objdir] key not in project')
        project.objdir = projectS['objdir']

        #################### NON ESSENTIALS ########################
        if 'location' in projectS.keys() and projectS['location'] != None :
            project.location = projectS['location']

        if 'defines' in projectS.keys() and projectS['defines'] != None :
            project.defines = projectS['defines']
        
        if 'files' in projectS.keys() and projectS['files'] != None :
            project.files = projectS['files']
        
        if 'includedirs' in projectS.keys() and projectS['includedirs'] != None :
            project.includedirs = projectS['includedirs']

        if 'linkdirs' in projectS.keys() and projectS['linkdirs'] != None :
            project.linkdirs = projectS['linkdirs']
        
        if 'linklibs' in projectS.keys() and projectS['linklibs'] != None :
            project.linklibs = projectS['linklibs']
        
        if 'linkprj' in projectS.keys() and projectS['linkprj'] != None :
            project.linkprj = projectS['linkprj']
        
        if 'outflags' in projectS.keys() and projectS['outflags'] != None :
            project.outflags = projectS['outflags']
        
        if 'intflags' in projectS.keys() and projectS['intflags'] != None :
            project.intflags = projectS['intflags']
        
        if 'onecompile' in projectS.keys() and projectS['onecompile'] != None :
            project.onecompile = projectS['onecompile']

        projects[project.name] = project
        

    workspace.projects = projects
    return workspace

    
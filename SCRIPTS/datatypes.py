class Project :
    name: str
    kind: str

    targetdir: str
    objdir: str
    
    location: str = ""
    defines: dict = []

    files: list[str] = [],
    includedirs: list[str] = []
    
    linkdirs: list[str] = []
    linklibs: list[str] = []
    linkprj: list = []

    outflags: str = ""
    intflags: str = ""
    output: str = ""

    LD_LIBS = ""
    onecompile: bool = False


class Workspace :
    name: str
    startup: str = ""
    statedir: str
    
    location: str = ""
    projects: list[Project] = []
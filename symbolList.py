

class SymbolItem(object):
    def __init__(self, name, _type, cat, addr):
        self.name = name
        self.type = _type
        self.cat = cat
        self.addr = addr

class SymbolList(object):
    def __init__(self):
        self.symbolList = []

class SymbolSystem(object):
    def __init__(self):
        self.activeLevel = 0
        self.curVarType = None
        self.curVarCat = None
        self.curValue = None
        self.curParamType = None
        self.curParamCat = None
        self.levelStack = []
        self.curVarStack = []
        self.curParamStack = []

    def find(self, name, level):
        """
        在指定层级查找符号,level = all or cur
        """
        findStack = []
        if level == 'cur':
            findStack = self.levelStack[self.activeLevel]
        elif level == 'all':
            findStack = self.levelStack[]
        else:
            # 报错
            pass

        for symList in findStack:
            for symItem in symList.symbolList:
                if symItem.name == name:
                    return symItem

    def insert(self):
        """
        变量声明时的插入函数
        """
        if 
        
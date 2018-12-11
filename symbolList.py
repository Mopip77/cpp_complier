

class FuncList(object):
    def __init__(self):
        self.offset = 2
        self.paramNum = 0
        self.paramList = []
        self.entry = 0


class SymbolItem(object):
    def __init__(self, name, _type, cat, addr):
        self.name = name
        self.type = _type
        self.cat = cat
        self.addr = addr


class SymbolList(object):
    def __init__(self, level):
        self.level = level
        self.nextLevelSL = None
        self.offset = 3
        self.curVarType = None
        self.curVarCat = None
        self.varStack = []
        self.symbolList = []


class SymbolListSystem(object):
    def __init__(self):
        baseLevelSL = SymbolList(0)
        self.levelStack = [baseLevelSL]
        self.activeSL = self.levelStack[-1]

    def find(self, name, level):
        """
        在指定层级查找符号,level = all or cur
        """
        findStack = []
        if level == 'cur':
            findStack = self.activeSL
        elif level == 'all':
            findStack = self.levelStack
        else:
            # 报错
            pass

        for symList in findStack:
            for symItem in symList.symbolList:
                if symItem.name == name:
                    return symItem
        return False

    def create_next_level(self):
        curLevel = self.levelStack[-1].level
        nextLevelSL = SymbolList(curLevel)
        self.levelStack[-1].nextLevelSL = nextLevelSL
        self.levelStack.append(nextLevelSL)
        self.activeSL = self.levelStack[-1]

    def destory_next_level(self):
        self.levelStack.pop()
        self.activeSL = self.levelStack[-1]

    def fill_list_from_stack(self, stacktype):
        if stacktype == 'var':
            while self.activeSL.varStack.__len__():
                var = self.activeSL.varStack[0]
                self.activeSL.varStack = self.activeSL.varStack[1:]
                var.addr = (self.activeSL.level, self.activeSL.offset)
                self.activeSL.offset += type_len(var.type)
                self.activeSL.symbolList.append(var)
        elif stacktype == 'param':
            # 反填函数形参个数
            curFuncItem = self.levelStack[-2].symbolList[-1]
            curFuncItem.addr.paramNum = self.activeSL.varStack.__len__()
            while self.activeSL.varStack.__len__():
                var = self.activeSL.varStack[0]
                self.activeSL.varStack = self.activeSL.varStack[1:]
                var.addr = (self.activeSL.level, self.activeSL.offset)
                self.activeSL.offset += type_len(var.type)
                self.activeSL.symbolList.append(var)
                curFuncItem.addr.paramList.append(var)


    def 

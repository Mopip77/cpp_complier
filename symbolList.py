

class TmpValue(object):
    def __init__(self):
        self.type = None
        self.

class FuncList(object):
    def __init__(self):
        self.offset = 2
        self.paramNum = 0
        self.paramList = []
        self.entry = 0
        self.nextLevelSL = None


class SymbolItem(object):
    def __init__(self, name, _type, cat, addr):
        self.name = name
        self.type = _type
        self.cat = cat
        self.addr = addr


class SymbolList(object):
    offsetDict = {
        'int': 2,
        'float': 4,
        'char': 1,
        'bool': 1,
    }
    def __init__(self, level):
        self.level = level
        self.offset = level + 3
        self.len = 0
        self.activeItem = None
        self.curVarType = None
        self.curVarCat = None
        self.symbolList = []
        self.nextLevelSL = None

    def fill_info_and_push_list(self):
        """
        将当前的符号项的type,cat,addr信息填完后入符号表
        """
        self.activeItem.type = self.curVarType
        self.activeItem.cat = self.curVarCat
        if self.curVarCat != 'f':
            self.activeItem.addr = (self.level, self.offset)
            self.offset += self.offsetDict[self.curVarType]
        self.symbolList.append(self.activeItem)


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
            findStack = [self.activeSL]
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
        curLevel = self.activeSL.level
        nextLevelSL = SymbolList(curLevel + 1)
        # 0级,当前函数生成addr并指向下一级
        if curLevel == 0:
            funcItem = self.activeSL.symbolList[-1]
            funcItem.addr = FuncList()
            funcItem.addr.level = curLevel + 1
            funcItem.addr.len = funcItem.addr.level + 3
            funcItem.addr.nextLevelSL = nextLevelSL

        else:
        # 其他级,当前活动表指向下一级
            self.levelStack[-1].nextLevelSL = nextLevelSL

        self.levelStack.append(nextLevelSL)
        self.activeSL = self.levelStack[-1]

    def destory_next_level(self):
        self.levelStack.pop()
        self.activeSL = self.levelStack[-1]

    def fill_param_in_funclist(self):
        funlist = self.levelStack[-2].symbolList[-1].addr
        for param in self.activeSL.symbolList:
            funlist.paramList.append(param)
            funlist.paramNum += 1


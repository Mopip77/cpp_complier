import sys
sys.path.append('..')
import os
from cifa import CiFa
from config import *
from myerror import UnaccpetSymbol, InvalidSymbol, SEMErr, IncorrectParamNum
from symbolList import FuncList, SymbolItem, ArrList


class TempVar(object):
    """
    临时变量类
    """
    def __init__(self, name, cat="temp"):
        self.name = name
        self.cat = cat
        self._type = None

    def __str__(self):
        return "%s" % self.name


class MiddleCode(object):
    """
    四元式类，存储自定义变量和临时变量都是存储相应类
    """
    def __init__(self, opt, item1=None, item2=None, res=None):
        self.opt = opt
        self.item1 = item1
        self.item2 = item2
        self.res = res

    # for test
    def __str__(self):
        if isinstance(self.item1, SymbolItem) or isinstance(self.item1, TempVar):
            item1 = self.item1.name
        else:
            item1 = self.item1
        if isinstance(self.item2, SymbolItem) or isinstance(self.item2, TempVar):
            item2 = self.item2.name
        else:
            item2 = self.item2
        if isinstance(self.res, SymbolItem) or isinstance(self.res, TempVar):
            res = self.res.name
        else:
            res = self.res
        return "%s %s %s %s" % (self.opt, item1, item2, res)


class LRDerveDictGerenator(object):
    """
    自动生成推断表
    """

    def __init__(self):
        # test用,记录读过的符号
        self.testStack = []
        self.stusNum = 0 # 项目集编号,每进入一个项目集+1
        self.chanshenshi = WENFA_DICT['chanshenshi']
        self.Vn = WENFA_DICT['vn']
        self.startVn = WENFA_DICT['startVn']
        self.endChar = ENDCHAR
        # 加入全局起始状态
        self.topStus = '#S'
        # 生成目标结果
        self.derveDict = {}  # 推断表
        self.guiyueListForSLR = {}  # 规约表给(SLR 用) (状态, 产生式元素的个数)

        self.__css_change_to_LR_format()

        self.Vt = self.__get_Vt()

        self.firstCharSet = self.__build_first_char_set()

        # 已经推出来了的状态集合 key=项目编号, value=项目集
        self.usedSetDict = {}

        # 产生式中加入top推导,至于为什么要在求first集合后,我给忘了
        self.chanshenshi[self.topStus] = [[self.startVn]]

        # 规约表(Here用) (状态, 产生式, 编号)
        self.guiyueList = []
        self.__generate_guiyue_list()

        # 可规约状态集合
        self.guiyueableStusDict = {}

    def __css_change_to_LR_format(self):
        """
        将产生式变成符合LR格式的文法,即动作在最后
        """
        tmpNum = 0
        tmpStus = 'tmpStus_{}'
        tmpStusReferDict = {}
        _tmpDict = {} # 扩展出来的文法,最后加入self.chanshenshi
        self._tmpEmptyStus = set() # 可推出空的临时变量,在求first集合的时候需要使用
        for stus in self.chanshenshi:
            for css in self.chanshenshi[stus]:
                for i in range(0, css.__len__()):
                    if i != css.__len__() - 1 and isinstance(css[i], tuple):
                        item = css[i]
                        if not item in tmpStusReferDict:
                            _tmp = tmpStus.format(tmpNum)
                            if item[0] in self.Vn and [] in self.chanshenshi[item[0]]:
                                self._tmpEmptyStus.add(_tmp)
                            tmpStusReferDict[item] = _tmp
                            tmpNum += 1
                            _tmpDict[_tmp] = [[item]]
                            self.Vn.add(_tmp)
                        else:
                            _tmp = tmpStusReferDict[item]
                        css.insert(i, _tmp)
                        css.remove(item)

        self.chanshenshi.update(_tmpDict)

    def __get_stus_name(self, stus):
        """
        状态可能包含语义动作,这个函数返回状态名称
        """
        if isinstance(stus, tuple):
            return stus[0]
        else:
            return stus

    def __build_first_char_set(self):
        """
        求得状态first集合
        """
        # test
        finished_vn = set()
        first = {}
        for i in self.Vn:
            first[i] = {'first': set(), 'vn': [], 'empty': False}

        # 为可空临时变量的'empty'属性赋值
        for emptyStus in self._tmpEmptyStus:
            first[emptyStus]['empty'] = True
        del self._tmpEmptyStus
        
        for stus in self.chanshenshi.keys():
            for css in self.chanshenshi[stus]:
                # 产生式非空
                if css.__len__():
                    pos = 0
                    firstChar = self.__get_stus_name(css[0])
                    # 首符号是终极符
                    if firstChar in self.Vt:
                        first[stus]['first'].add(firstChar)
                    # 首符号是非终极符
                    else:
                        tmp_vn_stack = []
                        while True:
                            try:
                                if firstChar in self.Vt:
                                    tmp_vn_stack.append(firstChar)
                                    break
                                if firstChar == stus:
                                    break
                                tmp_vn_stack.append(firstChar)                                
                                pos += 1
                                firstChar = self.__get_stus_name(css[pos])
                            # 产生式全为非终极符
                            except:
                                break
                        if tmp_vn_stack.__len__():
                        # 当 Z -> Z... 栈里不会有东西
                            first[stus]['vn'].append(tmp_vn_stack)
                            
                else:
                    first[stus]['empty'] = True

            # 该stus first集合求完毕
            if first[stus]['vn'].__len__() == 0:
                finished_vn.add(stus)

        # 循环解决剩余非终极符frist集合的填写, 每轮都得能推出东西
        solved_vn_num_cur_turn = True
        while True:
            if solved_vn_num_cur_turn is False:
                print('[*]求first集合有回环')
                os._exit(0)
            if self.Vn.__len__() == finished_vn.__len__():
                break
            solved_vn_num_cur_turn = False
            for stus in first.keys():
                if stus not in finished_vn:
                    # 这里需要删除self.firstCharSet[stus]['vn']中的产生式,如果直接删除遍历会跳过
                    # 用一个栈先代替
                    _tmpCssStack = []
                    _tmpCssStack += first[stus]['vn']
                    for css in first[stus]['vn']:
                        # 遍历vn
                        pos = 0
                        cur_vn = css[pos]
                        # 如果当前vn没被推出来
                        if cur_vn not in finished_vn:
                            continue
                        else:
                            def __add_first_set_obo(count):
                                for i in range(0, count+1):
                                    if css[i] in self.Vn:
                                        first[stus]['first'].update(first[css[i]]['first'])
                                    else:
                                        first[stus]['first'].add(css[i])
                                _tmpCssStack.remove(css)
                                # first[stus]['vn'].remove(css)
                                finished_vn.add(stus)

                        # 如果vn已经推出了的, 并且不可推出空
                            if first[cur_vn]['empty'] is False:
                                __add_first_set_obo(0)
                                solved_vn_num_cur_turn = True
                        # 如果vn已经推出了的, 并且可以推出空
                            else:
                                # 依次检查下一个
                                while True:
                                    pos += 1
                                    try:
                                        cur_vn = css[pos]
                                    except:
                                        # 越界说明全是vn，并且全能推出空
                                        __add_first_set_obo(pos-1)
                                        break
                                    # 下一个vn如果是是vt
                                    if cur_vn in self.Vt:
                                        __add_first_set_obo(pos)
                                        solved_vn_num_cur_turn = True
                                        break
                                    # 下一个如果能被退出来
                                    elif cur_vn in finished_vn:
                                        # 下一个能推出空
                                        if first[cur_vn]['empty'] is True:
                                            continue
                                        else:
                                            __add_first_set_obo(pos)
                                            solved_vn_num_cur_turn = True
                                            break
                                    #下一个不能推出来
                                    else:
                                        break
                    # 重置vn集合
                    first[stus]['vn'] = _tmpCssStack
                
        return first

    def __get_Vt(self):
        """
        获取所有的终极符
        """
        all_v = set()
        all_v.update(self.Vn)
        for cssEs in self.chanshenshi.values():
            for css in cssEs:
                if css.__len__():
                    all_v.update(set(css[:-1]))
                    if isinstance(css[-1], tuple):
                        all_v.add(css[-1][0])
                    else:
                        all_v.add(css[-1])
        all_v.add(self.endChar)
        return all_v - self.Vn

    def __generate_guiyue_list(self):
        """
        对每个产生式编号,并且生成本自动器规约表, SLR规约表
        SLR规约表格式 {stus:(firstStus, chanshenshi_num)}
        本自动器规约表格式(stus, chanshenshi, No.)
        """
        num = 0
        for stus in self.chanshenshi.keys():
            for chanshenshi in self.chanshenshi[stus]:
                self.guiyueList.append((stus, chanshenshi, num))
                self.guiyueListForSLR[num] = (stus, chanshenshi.__len__())
                num += 1

    def __get_chanshenshi_num(self, stus, cs):
        """
        由产生式得到编号,stus是推导首产生式,cs是产生式列表
        """
        i = 0
        for g in self.guiyueList:
            if g[0] == stus and g[1] == cs:
                return i
            i += 1
        print('找不到该产生式的编号')
        os._exit(0)

    def get_num_chanshenshi(self, num):
        """
        由编号得到产生式
        """
        return self.guiyueList[num][1]

    def __get_num_stus(self, num):
        """
        由编号得到产生状态
        """
        return self.guiyueList[num][0]

    def __get_next_stus_set(self, curStusSet):
        """
        传入当前项目集, 返回当前项目集编号
        """
        # 当前层级编号
        # 查重
        theSame = True
        for num in self.usedSetDict:
            if self.usedSetDict[num].__len__() == curStusSet.__len__():
                theSame = True
                for i in range(0, curStusSet.__len__()):
                    if self.usedSetDict[num][i] != curStusSet[i]:
                        theSame = False
                        break
                if theSame:
                    return num
 
        curStusNum = self.stusNum
        self.testStack.append(curStusNum)
        self.stusNum += 1
        self.derveDict[curStusNum] = {}
        self.usedSetDict[curStusNum] = curStusSet
        # 分类读取的字符
        _readCharDict = {}
        for item in curStusSet:
            try:
                readChar = self.__get_stus_name(
                    self.get_num_chanshenshi(item[0][0])[item[0][1]])
            except IndexError:
                # 规约状态
                for endChar in item[1]:
                    if endChar not in self.derveDict[curStusNum].keys():
                        self.derveDict[curStusNum][endChar] = ('r', item[0][0])
                    else:
                        print('[*]规约规约冲突...')
                        os._exit(0)
            else:
                if readChar not in _readCharDict.keys():
                    _readCharDict[readChar] = []
                # 变成读取下一状态
                _nextItem = ((item[0][0], item[0][1] + 1), item[1])
                _readCharDict[readChar].append(_nextItem)
        
        for readChar in _readCharDict:
            # 派生产生式
            fir = self.__expand_css(_readCharDict[readChar])
            # 连接下一个状态
            nextStusNum = self.__get_next_stus_set(fir)
            self.derveDict[curStusNum][readChar] = nextStusNum

        # 可能本状态集合也能推出空
        if curStusNum in self.guiyueableStusDict:
            guiyueStus = self.guiyueableStusDict[curStusNum][0]
            for endChar in self.guiyueableStusDict[curStusNum][1]:
                if endChar not in self.derveDict[curStusNum]:
                    self.derveDict[curStusNum][endChar] = ('r', guiyueStus)
                else:
                    pass
                    # 这里出现了4个冲突情况,都是调用函数的时候
                    # print(curStusNum, guiyueStus, endChar)
                    # print(self.testStack)
                    # print('规约移进冲突')
                    # os._exit(0)
        self.testStack.pop()
        return curStusNum

    def __expand_css(self, curCssList):
        """
        扩充项目集的当前读取的非终极符,返回项目集
        """
        cssStack = []
        generStack = []
        cssStack += curCssList  # 当前项目集所有产生式
        generStack += curCssList  # 当前项目集需要扩充的产生式

        while generStack.__len__():
            tmpStus = generStack.pop()
            try:
                css = self.get_num_chanshenshi(tmpStus[0][0])
                readChar = self.__get_stus_name(css[tmpStus[0][1]])
            except IndexError:
                # 最后一个
                continue
            else:
                if readChar in self.Vn:
                    # 找到此产生式推导出的产生式的规约符号集合
                    firstSet = set()
                    if css.__len__() == tmpStus[0][1] + 1:
                        # 该符号是产生式的最后一个
                        firstSet.update(tmpStus[1])
                    else:
                        _nextStusSet = self.__get_stus_name(css[tmpStus[0][1] + 1])
                        if _nextStusSet in self.Vn:
                            firstSet.update(self.firstCharSet[_nextStusSet]['first'])
                            if self.firstCharSet[_nextStusSet]['empty'] is True:
                                # 如果该非终极符是可空状态
                                pos = 1
                                while True:
                                    pos += 1
                                    try:
                                        # 继续找下一个
                                        _s = self.__get_stus_name(css[tmpStus[0][1] + pos])
                                    except IndexError:
                                        # 读完了,则加上tmpStus的followset
                                        firstSet.update(tmpStus[1])
                                        break
                            
                                    if _s not in self.Vn:
                                        firstSet.add(_s)
                                        break
                                    else:
                                        firstSet.update(self.firstCharSet[_s]['first'])
                                        if self.firstCharSet[_s]['empty'] is False:
                                            break
                        else:
                            firstSet.add(_nextStusSet)
        
                    # 找到所有派生出的产生式
                    for css in self.chanshenshi[readChar]:
                        if css.__len__() == 0:
                            # 当前项目集可推出空,登记到可规约状态表
                            emptyCssNum = self.__get_chanshenshi_num(readChar, css)
                            self.guiyueableStusDict[self.stusNum] = (emptyCssNum, firstSet)
                        else:
                            # 去左递归
                            curStus = (self.__get_chanshenshi_num(readChar, css), 0)
                            curStusHasChanged = False
                            for i in cssStack:
                                if curStus == i[0]:
                                    curStusHasChanged = True
                                    if firstSet | i[1] != i[1]:
                                        # 规约状态有更新
                                        tmpSet = set()
                                        tmpSet.update(firstSet)
                                        tmpSet.update(i[1])
                                        if i in generStack:
                                            generStack.remove(i)
                                        # 将更新的状态放到两个栈中
                                        cssStack.insert(0, (curStus, tmpSet))
                                        generStack.insert(0, (curStus, tmpSet))
                                        # 移除项目集中更新前的状态
                                        cssStack.remove(i)
                                    break
                            if not curStusHasChanged:
                                # 没更改即栈中没有,插入
                                cssStack.insert(0, (curStus, firstSet))
                                generStack.insert(0, (curStus, firstSet))
        return cssStack

    def generate(self):
        """
        生成LR表
        """
        _topNum = self.__get_chanshenshi_num(self.topStus, [self.startVn])
        fir = self.__expand_css([((_topNum, 0), set(self.endChar))])
        self.__get_next_stus_set(fir)
        # 修改完成状态
        self.derveDict[0][self.startVn] = True
        # 删除无用状态
        del self.testStack
        del self.firstCharSet
        del self.guiyueableStusDict
        del self.stusNum
        del self.usedSetDict
        del self.topStus


class LR(LRDerveDictGerenator):
    def __init__(self):
        super(LR, self).__init__()
        self.generate()
        # while True:
        #     self.guiyueList
        #     s = input()
        #     print(self.derveDict[int(s)])
        self.cifa = CiFa(ALL_STARTSTATUS, ALL_STATUS, ALL_DERVEDICT,
                         ALL_ENDSTATUS, 'v.cpp')
        self.stusStack = []
        self.token = tuple()
        # 使用函数参数个数检查, 由于参数能嵌套函数,所以用一个栈
        self.funcParamCountStack = []

        # 四元式
        self.tmpVarFormat = "t{}"
        self.tmpNum = 1
        self.SEMStack = []
        self.QT = []

    def __get_next_token(self):
        self.token = self.cifa.get_next_token()

    def __transCurSymbol(self):
        """
        变换当前字符为终极符
        """
        # 标识符常数
        if self.token[0] == 'c':
            return '<常数>'
        elif self.token[0] == 'i':
            if self.token[1].addr is None:
                return '<未定义标识符>'
            elif isinstance(self.token[1].addr, FuncList):
                return '<函数标识符>'
            elif self.token[1].cat == 'arr':
                return '<数组标识符>'
            else:
                return '<非函数标识符>'
        # 界符
        elif self.token[0] == 'p' or self.token[0] == 'k':
            symbol = self.cifa.symbolList[self.token[0]][self.token[1]]
            if symbol == '+' or symbol == '-':
                return '<+->'
            elif symbol == '*' or symbol == '/':
                return '<*/>'
            # elif symbol in ['>=', '<=', '==', '>', '<']:
            #     return '<逻辑运算符>'
            elif symbol in ['int', 'float', 'char', 'bool']:
                return '<类型>'
            else:
                return symbol
        # 结束符
        elif self.token[0] == 'end':
            return self.cifa.symbolList[self.token[0]][self.token[1]]
        # 不接受的字符
        else:
            raise InvalidSymbol(
                self.cifa.symbolList[self.token[0]][self.token[1]])

    def __excute_lang_action(self, actions):
        """
        执行语义动作,传入动作集合
        """
        def get_a_tmp_value():
            _tmp = TempVar(self.tmpVarFormat.format(self.tmpNum))
            self.tmpNum += 1
            return _tmp

        for act in actions:
            if act == 1:
                self.cifa.SL.activeSL.curVarType = self.stusStack[-1][0]
            elif act == 2:
                self.cifa.SL.activeSL.curVarCat = 'v'
            elif act == 3:
                self.cifa.SL.create_next_level()
            elif act == 4:
                self.cifa.SL.activeSL.curVarCat = 'f'
            elif act == 5:
                self.cifa.SL.destory_next_level()
            elif act == 6:
                self.cifa.SL.activeSL.curVarCat = 'arr'
            elif act == 7:
                self.cifa.SL.activeSL.curVarType = self.stusStack[-1][0]
                self.cifa.SL.activeSL.curVarCat = 'vn'
            elif act == 8:
                self.cifa.SL.activeSL.fill_info_and_push_list()
            elif act == 9:
                self.cifa.SL.fill_param_in_funclist()
            elif act == 10:
                self.token = ('i', self.cifa.SL.new_symbol_item(self.token[1]))
            elif act == 11:
                filename = self.SEMStack.pop()
                if isinstance(filename, SymbolItem):
                    filename = filename.name + '.c'
                    self.cifa.insert_file_content(filename)
            elif act == 12:
                self.cifa.SL.activeSL.activeItem.addr.levelLenList.append(self.stusStack[-1][0])
            elif act == 13:
                self.cifa.SL.activeSL.activeItem.addr.cal_total_len()
            elif act == 14:
                self.funcParamCountStack.append(self.SEMStack[-1].addr.paramNum)
            elif act == 'A':
                self.SEMStack.append(self.stusStack[-1][0])
            elif act == 'B':
                if self.funcParamCountStack[-1] != 0:
                    needParamNum = self.SEMStack[-1].addr.paramNum
                    givenParamNum = needParamNum - self.funcParamCountStack[-1]
                    raise IncorrectParamNum('函数', self.SEMStack[-1].name, needParamNum, givenParamNum)
                self.funcParamCountStack.pop()
                funcItem = self.SEMStack.pop()
                _tmpVar = get_a_tmp_value()
                qt = MiddleCode("call", funcItem, None, _tmpVar)
                self.QT.append(qt)
                self.SEMStack.append(_tmpVar)
            elif act == 'C':
                retVar = self.SEMStack.pop()
                qt = MiddleCode("ret", retVar, None, None)
                self.QT.append(qt)
            elif act == 'D':
                qt = MiddleCode("ie", None, None, None)
                self.QT.append(qt)
            elif act == 'E':
                qt = MiddleCode("el", None, None, None)
                self.QT.append(qt)
            elif act == 'F':
                judgeVar = self.SEMStack.pop()
                qt = MiddleCode("if", judgeVar, None, None)
                self.QT.append(qt)
            elif act == 'G':
                qt = MiddleCode("wh", None, None, None)
                self.QT.append(qt)
            elif act == 'H':
                item1 = self.SEMStack.pop()
                opt = self.SEMStack.pop()
                item2 = self.SEMStack.pop()
                _tmpVar = get_a_tmp_value()
                qt = MiddleCode(opt, item2, item1, _tmpVar)
                self.QT.append(qt)
                self.SEMStack.append(_tmpVar)
            elif act == 'I':
                item = self.SEMStack.pop()
                _tmpStack = [item]
                while True:
                    item = self.SEMStack.pop()
                    _tmpStack.insert(0, item)
                    if isinstance(item, SymbolItem) and item.cat == 'arr':
                        break
                # 数组参数个数分析
                needNum = item.addr.levelLenList.__len__()
                givenNum = _tmpStack.__len__() - 1
                if needNum != givenNum:
                    raise IncorrectParamNum('数组', item.name, needNum, givenNum)
                self.SEMStack.append(tuple(_tmpStack))
            elif act == 'J':
                outVar = self.SEMStack.pop()
                qt = MiddleCode("out", None, None, outVar)
                self.QT.append(qt)
            elif act == 'K':
                self.SEMStack.pop()
            elif act == 'L':
                self.funcParamCountStack[-1] -= 1
                param = self.SEMStack.pop()
                qt = MiddleCode("param", param, None, None)
                self.QT.append(qt)
            elif act == 'M':
                judgeVar = self.SEMStack.pop()
                qt = MiddleCode("do", judgeVar, None, None)
                self.QT.append(qt)
            elif act == 'N':
                qt = MiddleCode("we", None, None, None)
                self.QT.append(qt)
            elif act == 'P':
                qt = MiddleCode("pe", None, None, None)
                self.QT.append(qt)
            elif act == 'Q':
                item = self.SEMStack[-1]
                qt = MiddleCode("=", 0, None, item)
                self.QT.append(qt)
            elif act == 'R':
                value = self.SEMStack.pop()
                target = self.SEMStack.pop()
                qt = MiddleCode('=', value, None, target)
                self.QT.append(qt)
            elif act == 'T':
                funcName = self.SEMStack.pop()
                qt = MiddleCode("pro", funcName, None, None)
                self.QT.append(qt)

    def __guiyue(self, nS):
        """
        规约，同时执行相应的语义动作
        """
        g = self.guiyueListForSLR[nS[1]]  # nS[1]规约生成式的编号
        guiyueName = g[0]
        guiyueCount = g[1]
        # action
        css = self.get_num_chanshenshi(nS[1])
        if css.__len__() and isinstance(css[-1], tuple):
            actions = css[-1][1]
            self.__excute_lang_action(actions)

        if guiyueCount != 0:
            self.stusStack = self.stusStack[:(-1 * guiyueCount)]
        nS = self.derveDict[self.stusStack[-1][1]][guiyueName]
        self.stusStack.append((guiyueName, nS))

    def token_to_word(self):
        """
        返回当前token实际的单词
        """
        if isinstance(self.token[1], int):
            return self.cifa.symbolList[self.token[0]][self.token[1]]
        else:
            return self.token[1].name

    def run(self):
        try:
            self.stusStack.append((self.endChar, 0))
            self.__get_next_token()

            while True:
                curStus = self.stusStack[-1][1]
                # if curStus in [58, 60, 101, 140]:
                #     print('bad...')
                #     print(self.stusStack)

                w = self.__transCurSymbol()
                print(w, self.token_to_word())

                if curStus is True:
                    for i in self.QT:
                        print(i)
                    print('[*]当前识别串符合该文法')
                    return True
                elif w not in self.derveDict[curStus].keys():
                    firstList = list(self.derveDict[self.stusStack[-1][1]].keys())
                    raise UnaccpetSymbol(self.stusStack[-1][0], '{}({})'.format(self.token_to_word(), w), \
                                            firstList)
                else:
                    nS = self.derveDict[curStus][w]
                    # 压栈
                    if isinstance(nS, int):
                        if isinstance(self.token[1], int):
                            curWord = self.token_to_word()
                        else:
                            curWord = self.token[1]
                        self.stusStack.append((curWord, nS))
                        self.__get_next_token()
                    # 规约
                    else:
                        self.__guiyue(nS)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    v = LR()
    v.run()

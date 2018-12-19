import sys
sys.path.append('..')
import os
from cifa import CiFa
from config import *
from myerror import err1, InvalidSymbol, SEMErr, ReDefined
from symbolList import FuncList, SymbolItem
# from tmpvalue import TmpValue


class TmpValue(object):
    pass


class DerveDictGererator(object):
    """
    自动生成推断表
    """

    def __init__(self):
        self.testStack = []
        self.stusNum = 0
        # 外部输入，这里没分离
        # 输入产生式
        # self.chanshenshi = {
        #     '运算表达式': [['项'], ['运算表达式', 'w0', ('项', ('gen', 'w0'))]],
        #     '项': [['因子'], ['项', 'w1', ('因子', ('gen', 'w1'))]],
        #     '因子': [['运算对象'], ['(', '运算表达式', ')']],
        #     '运算对象': [[('函数标识符', ('push', 'i')), '(', ')'], [('非函数标识符', ('push', 'i'))], [('常数', ('push', 'i'))]]    
        # }
        # # 输入非终极符, 起始符号, 结束符号
        # self.Vn = {'运算表达式', '项', '因子', '运算对象'}
        # self.startVn = '运算表达式'
        # self.endChar = '#'
        self.chanshenshi = yufa_1['chanshenshi']
        self.Vn = yufa_1['vn']
        self.startVn = yufa_1['startVn']
        self.endChar = yufa_1['endChar']
        # 加入全局起始状态
        self.topStus = '#S'
        # 生成目标结果
        self.derveDict = {}  # 推断表
        self.guiyueListForSLR = {}  # 规约表给(SLR 用) (状态, 产生式元素的个数)

        self.__css_change_to_LR_format()

        self.Vt = self.__get_Vt()

        self.firstCharSet = self.__build_first_char_set()

        self.usedSetDict = {}

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
        for stus in self.chanshenshi:
            for css in self.chanshenshi[stus]:
                for i in range(0, css.__len__()):
                    if i != css.__len__() - 1 and isinstance(css[i], tuple):
                        item = css[i]
                        if not item in tmpStusReferDict:
                            _tmp = tmpStus.format(tmpNum)
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
                                first[stus]['vn'].remove(css)
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

        return first

    def __get_Vt(self):
        all_v = set()
        all_v.update(self.Vn)
        for i in self.chanshenshi.values():
            for v in i:
                if v.__len__():
                    all_v.update(set(v[:-1]))
                    if isinstance(v[-1], tuple):
                        all_v.add(v[-1][0])
                    else:
                        all_v.add(v[-1])
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
        由产生式得到编号
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
                # self.guiyueableStusDict.add(item[0])
                for endChar in item[1]:
                    if endChar not in self.derveDict[curStusNum].keys():
                        self.derveDict[curStusNum][endChar] = ('r', item[0][0])
                    else:
                        print('规约冲突')
                        os._exit()
            else:
                if readChar not in _readCharDict.keys():
                    _readCharDict[readChar] = []
                # 变成读取下一状态
                _nextItem = ((item[0][0], item[0][1] + 1), item[1])
                _readCharDict[readChar].append(_nextItem)
        
        for readChar in _readCharDict:
            # 派生产生式
            fir = self.__expand_css(_readCharDict[readChar])
            # 自己到自己
            theSameStus = True
            for i in range(0, fir.__len__()):
                if fir[i][0] != curStusSet[i][0]:
                    theSameStus = False
                    break
            # 链接两个状态
            nextStusNum = self.__get_next_stus_set(fir)
            self.derveDict[curStusNum][readChar] = nextStusNum

        # 可能本状态集合也能推出空
        if curStusNum in self.guiyueableStusDict:
            guiyueStus = self.guiyueableStusDict[curStusNum][0]
            for endChar in self.guiyueableStusDict[curStusNum][1]:
                if endChar not in self.derveDict[curStusNum]:
                    self.derveDict[curStusNum][endChar] = ('r', guiyueStus)
                else:
                    print(curStusNum, guiyueStus, endChar)
                    # os._exit(0)
        self.testStack.pop()
        return curStusNum

    def __expand_css(self, curCssList):
        cssStack = []
        generStack = []
        cssStack += curCssList
        generStack += curCssList

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
                    # 找到此产生式的后继符
                    # 该符号是产生式的最后一个
                    firstSet = set()
                    if css.__len__() == tmpStus[0][1] + 1:
                        firstSet.update(tmpStus[1])
                    else:
                        _nextStusSet = self.__get_stus_name(css[tmpStus[0][1] + 1])
                        if _nextStusSet in self.Vn:
                            firstSet.update(self.firstCharSet[_nextStusSet]['first'])
                            # 如果后面是可空状态
                            if self.firstCharSet[_nextStusSet]['empty'] is True:
                                pos = 1
                                while True:
                                    pos += 1
                                    try:
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
                            # cssStack.append((None, firstSet))
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
                                        # firstSet.update(i[1])
                                        if i in generStack:
                                            generStack.remove(i)
                                        cssStack.insert(0, (curStus, tmpSet))
                                        generStack.insert(0, (curStus, tmpSet))
                                        # firstSet ^= i[1]
                                        cssStack.remove(i)
                                    break
                            if not curStusHasChanged:
                                cssStack.insert(0, (curStus, firstSet))
                                generStack.insert(0, (curStus, firstSet))
        return cssStack

    def generate(self):
        _topNum = self.__get_chanshenshi_num(self.topStus, [self.startVn])
        fir = self.__expand_css([((_topNum, 0), set(self.endChar))])
        self.__get_next_stus_set(fir)
        # 修改完成状态
        self.derveDict[0][self.startVn] = True
        # 删除无用状态
        del self.firstCharSet
        del self.guiyueableStusDict
        del self.stusNum
        del self.usedSetDict
        del self.topStus


class SLR(DerveDictGererator):
    def __init__(self):
        super(SLR, self).__init__()
        self.generate()
        print(1)
        # while True:
        #     self.guiyueList
        #     s = input()
        #     print(self.derveDict[int(s)])
        self.cifa = CiFa(ALL_STARTSTATUS, ALL_STATUS, ALL_DERVEDICT,
                         ALL_ENDSTATUS, 'v.cpp')
        self.stack = []
        self.token = tuple()

        self.SEM = []
        self.QT = []

    def __get_next_token(self):
        self.token = self.cifa.get_next_token()
        # 读完
        # if self.token is False:
        #     self.token = self.endChar

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
            else:
                return '<非函数标识符>'
        # 界符
        elif self.token[0] == 'p' or self.token[0] == 'k':
            symbol = self.cifa.symbolList[self.token[0]][self.token[1]]
            if symbol == '+' or symbol == '-':
                return '<+->'
            elif symbol == '*' or symbol == '/':
                return '<*/>'
            elif symbol in ['>=', '<=', '==', '>', '<']:
                return '<逻辑运算符>'
            elif symbol in ['int', 'float', 'char', 'bool']:
                return '<类型>'
            else:
                return symbol
            # else:
            #     raise InvalidSymbol(
            #         self.cifa.symbolList[self.token[0]][self.token[1]])
        # 结束符
        elif self.token == self.endChar:
            return self.token
        # 不接受的字符
        else:
            raise InvalidSymbol(
                self.cifa.symbolList[self.token[0]][self.token[1]])

    def __generate_qurt(self, symbol):
        """ 
        生成四元式
        """
        if self.SEM.__len__() < 2:
            raise SEMErr
        else:
            y = self.SEM.pop()
            x = self.SEM.pop()
            b = TmpValue()
            self.QT.append((symbol, x, y, b))
            self.SEM.append(b)

    def __excute_lang_action(self, actions):
        for act in actions:
            if act == 2:
                self.cifa.SL.activeSL.curVarCat = 'v'
            if act == 10:
                if self.cifa.SL.find(self.token[1].name, 'cur') is not False:
                    raise ReDefined(self.token[1].name)
                self.cifa.SL.activeSL.curVarType = self.stack[-1][0]
            elif act == 8:
                self.cifa.SL.activeSL.fill_info_and_push_list()
            

    def __guiyue(self, nS):
        """
        规约，同时执行相应的语义动作
        """
        g = self.guiyueListForSLR[nS[1]]  # nS[1]规约生成式的编号
        guiyueName = g[0]
        guiyueCount = g[1]
        # action
        try:
            css = self.get_num_chanshenshi(nS[1])
            if css.__len__() and isinstance(css[-1], tuple):
                actions = css[-1][1]
                self.__excute_lang_action(actions)
        except Exception as e:
            print(e)
            os._exit(0)

        if guiyueCount != 0:
            self.stack = self.stack[:(-1 * guiyueCount)]
        nS = self.derveDict[self.stack[-1][1]][guiyueName]
        self.stack.append((guiyueName, nS))

    def token_to_word(self):
        if isinstance(self.token[1], int):
            return self.cifa.symbolList[self.token[0]][self.token[1]]
        else:
            return self.token[1].name

    def run(self):
        self.stack.append((self.endChar, 0))
        self.__get_next_token()

        # test
        testStack = []

        while True:
            curStus = self.stack[-1][1]
            # testStack.append(curStus)

            w = self.__transCurSymbol()
            print(w, self.token_to_word())

            if curStus is True:
                for i in self.QT:
                    print(i)
                print('[*]当前识别串符合该文法')
                return True
            elif w not in self.derveDict[curStus].keys():
                raise err1
            else:
                nS = self.derveDict[curStus][w]
                # 压栈
                if isinstance(nS, int):
                    if isinstance(self.token[1], int):
                        wD = self.token_to_word()
                    else:
                        wD = self.token[1]
                    self.stack.append((wD, nS))
                    self.__get_next_token()
                # 规约
                else:
                    self.__guiyue(nS)


if __name__ == "__main__":
    v = SLR()
    v.run()

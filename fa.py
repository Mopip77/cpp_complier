from config import *
from myerror import UnaccpetChar, InvalidSymbol


class FA(object):
    '''
    五元组自动机
    '''

    def __init__(self, startstatus, status, dervedict, endstatus, checkingstr):
        self.startStus = startstatus  # 开始状态
        self.status = status  # 所有状态
        self.curStus = self.startStus  # 当前状态
        self.derveDict = dervedict  # 状态转移表
        self.endStus = endstatus  # 结束状态
        self.curPos = 0
        self.checkingStr = checkingstr
        self.curChar = self.checkingStr[0]

    def is_vaild_symbol(self, Char):
        c = Char
        if not (c <= 'Z' or c >= 'A'):
            if not (c <= 'Z' or c >= 'A'):
                if not (c <= '9' or c >= '0'):
                    if c not in p_LIST or c != '#':
                        return False
        return True

    # 返回下一个字符，文件读完返回False
    def get_next_char(self):
        try:
            self.curPos += 1
            self.curChar = self.checkingStr[self.curPos]
            return True
        # 读完
        except IndexError:
            return False

    def next_status(self):
        """
        读取并返回下一个状态，如果是结束状态返回True,出错则返回false
        """
        cC = self.curChar
        # 下一个状态对应列表,若没有则不接受任何状态，即结束状态
        try:
            dic = self.derveDict[self.curStus]
        except KeyError:
            return True
        # 当前字符是数字且有对应
        if (cC <= '9' and cC >= '0') and 'd' in dic:
            return dic['d']
        # 当前字符是字母且有对应
        elif (cC <= 'z' and cC >= 'a'
              or cC <= 'Z' and cC >= 'A') and 'l' in dic:
            return dic['l']
        # 当前字符是回车换行且有对应（只能是1状态）
        elif (cC == '\n' or cC == '\r' or cC == ' ' or cC == '\t') and 'n' in dic:
            return dic['n']
        # 其他符号且有对应
        elif cC in dic:
            return dic[cC]
        # 其他符号，没对应
        else:
            # 可结束
            if self.curStus in self.endStus:
                return True
            # 不可结束，出错
            else:
                self.my_error()

    def my_error(self):
        # 出错，若该符号属于符号表,属于状态不接受字符
        if self.is_vaild_symbol(self.curChar):
            raise UnaccpetChar(self.curStus, self.curChar)
        # 无效字符
        else:
            raise InvalidSymbol(self.curChar)


class MathFa(FA):
    def __init__(self, startstatus, status, dervedict, endstatus, checkingstr):
        super(MathFa, self).__init__(startstatus, status, dervedict, endstatus,
                                     checkingstr)
        self.curNum = 0
        self.offsetDot = 1
        self.sciCount = 0

    # 每次被调用初始化参数
    def _reload(self, curPos, curStus):
        self.curPos = curPos
        self.curChar = self.checkingStr[curPos]
        self.curStus = curStus
        self.curNum = 0
        self.offsetDot = 1
        self.sciCount = 0

    # 返回符合语法的下一个数字,返回值
    def get_next_num(self, curPos, curStus, checkingStr):
        self.checkingStr = checkingStr
        self._reload(curPos, curStus)
        while True:
            self._real_num_joint()
            # 找到下一状态
            nS = super().next_status()
            # 自动机结束
            if isinstance(nS, bool):
                if nS is True:
                    return self._real_num_count()
                else:
                    self.my_error()
            # 转移到下一状态
            self.curStus = nS
            # 文件读完
            if not self.get_next_char():
                if self.curStus in self.endStus:
                    return self._real_num_count()
                else:
                    self.my_error()

    def _real_num_count(self):
        #  当状态是3实数，7的时候为小数,31（正）、32（负）为科学计数
        if self.curStus == 3:
            n = self.curNum
        elif self.curStus == 7:
            n = self.curNum / self.offsetDot
        elif self.curStus == 31:
            for i in range(0, self.sciCount):
                self.offsetDot /= 10
            n = self.curNum / self.offsetDot
        elif self.curStus == 32:
            for i in range(0, self.sciCount):
                self.offsetDot *= 10
            n = self.curNum / self.offsetDot
        return n

    def _real_num_joint(self):
        # 由于规约的时候也要计算，所以要去除多余非数字字符
        try:
            n = int(self.curChar)
            # 当前状态3，7，8为底数，curNum为0时是状态1->3的时候
            if (
                    not self.curNum
            ) or self.curStus == 3 or self.curStus == 7 or self.curStus == 8:
                self.curNum = self.curNum * 10 + n
        # 当前字符不是数字
        except SyntaxError:
            return
        except ValueError:
            return
        else:
            cS = self.curStus
            # 7，8是有小数点的状态(正)
            if cS == 7 or cS == 8:
                self.offsetDot *= 10
            # 31是科学记数法为(正) 32是科学记数法为(负)
            # 30 -> 31 还一个数字
            elif cS == 31 or cS == 32 or cS == 30:
                self.sciCount = self.sciCount * 10 + n


class AllFA(FA):
    '''
    处理所有字符串
    '''

    def __init__(self, startstatus, status, dervedict, endstatus, checkingstr):
        super(AllFA, self).__init__(startstatus, status, dervedict, endstatus,
                                    checkingstr)
        self.curStr = ''
        self.strLen = len(self.checkingStr) - 1
        self.MAF = MathFa(MATH_STARTSTATUS, MATH_STATUS, MATH_DERVEDICT,
                          MATH_ENDSTATUS, checkingstr)

    def get_next_str(self):
        """
        返回下一个符合自动机规则的字符串
        """
        self.curStr = ''
        while True:
            # 找到下一状态
            nS = self.next_status()
            
            # 结束
            if nS is True:
                return self.curStr
            
            # 如果遇到实数状态进入实数状态识别
            if nS == MATH_CONDITION:
                num = self.MAF.get_next_num(self.curPos, self.curStus, self.checkingStr)
                # 同步变量
                self.curPos = self.MAF.curPos
                self.curChar = self.MAF.curChar
                self.curStus = self.MAF.curStus
                return num
            # 当遇到注释时过滤到换行为止
            elif nS == COMMENT_CONDITION:
                self.curStus = 1
                self.curStr = ''
                while True:
                    self.get_next_char()
                    if self.curChar == '\n':
                        self.get_next_char()
                        break
                    # 注释在最后一行
                    elif self.curChar == ENDCHAR:
                        # curStus置成结束符状态33
                        self.curStus = 33
                        return ENDCHAR
                continue

            # 将当前字符(非空，非回车换行)加到当前识别的字符串中
            if self.curChar not in [' ', '\n', '\r', '\t']:
                self.curStr += self.curChar
            # 进入下一个状态
            self.curStus = nS
            # 文件读完
            if not self.get_next_char():
                if self.curStus in self.endStus:
                    return self.curStr
                else:
                    self.my_error()

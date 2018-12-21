from symbolList import SymbolItem

class UnaccpetSymbol(Exception):
    def __init__(self, stus, Char, firstList):
        msg = self.differ_stus_type(stus)
        err = "[*]语法分析异常,当前{}不接受当前符号{}\n当前{}仅接收{}".format(msg, Char, msg, str(firstList)[1:-1])
        super(UnaccpetSymbol, self).__init__(err)

    def differ_stus_type(self, stus):
        _dict = {
            'arr': '数组',
            'f': '函数',
            'v': '变量',
            None: '<未定义标识符>'
        }
        if isinstance(stus, SymbolItem):
            message = _dict[stus.cat] + stus.name
        elif isinstance(stus, int):
            message = '常数' + str(stus) 
        else:
            message = '状态' + stus
        return message
                

class UnaccpetChar(Exception):
    def __init__(self, stus, Char):
        err = "[*]词法分析异常,当前状态{}不接受当前字符'{}'".format(stus, Char)
        super(UnaccpetChar, self).__init__(err)


class IncorrectParamNum(Exception):
    def __init__(self, _type, name, needNum, givenNum):
        err = "[*]参数个数错误...{}'{}'需要{}个参数,程序却给出{}个参数".format(_type, name, needNum, givenNum)
        super(IncorrectParamNum, self).__init__(err)


class InvalidSymbol(Exception):
    def __init__(self, Char):
        err = "[*]词法分析异常,当前字符'%s'为无效字符" % Char
        super(InvalidSymbol, self).__init__(err)


class SEMErr(Exception):
    def __init__(self):
        err = "[*]语义分析异常,语义栈运算成员不够"
        super(SEMErr, self).__init__(err)


class UnDefined(Exception):
    def __init__(self, Char):
        err = "[*]语义分析异常,当前字符'{}'未定义".format(Char)
        super(UnDefined, self).__init__(err)


class err0(Exception):
    def __init__(self):
        err = "[*]err0"
        super(err0, self).__init__(err)


class err1(Exception):
    def __init__(self):
        err = "[*]err1"
        super(err1, self).__init__(err)


class err2(Exception):
    def __init__(self):
        err = "[*]err2"
        super(err2, self).__init__(err)


class err3(Exception):
    def __init__(self):
        err = "[*]err3"
        super(err3, self).__init__(err)

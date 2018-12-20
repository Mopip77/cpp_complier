class UnaccpetSymbol(Exception):
    def __init__(self, stus, Char):
        err = "[*]捕获异常,当前状态{}不接受当前字符{}".format(stus, Char)
        super(UnaccpetSymbol, self).__init__(err)


class IncorrectParamNum(Exception):
    def __init__(self, _type, name, needNum, givenNum):
        err = "[*]参数个数错误...{}{}需要{}个参数,程序却给出{}个参数".format(_type, name, needNum, givenNum)
        super(IncorrectParamNum, self).__init__(err)


class InvalidSymbol(Exception):
    def __init__(self, Char):
        err = "[*]捕获异常,当前字符%s为无效字符" % Char
        super(InvalidSymbol, self).__init__(err)


class SEMErr(Exception):
    def __init__(self):
        err = "[*]捕获异常,语义栈运算成员不够"
        super(SEMErr, self).__init__(err)

class ReDefined(Exception):
    def __init__(self, Char):
        err = "[*]捕获异常,当前字符{}重定义".format(Char)
        super(ReDefined, self).__init__(err)

class UnDefined(Exception):
    def __init__(self, Char):
        err = "[*]捕获异常,当前字符{}未定义".format(Char)
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

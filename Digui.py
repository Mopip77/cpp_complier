from cifa import CiFa
from config import *
from symbolList import SymbolItem


class TempVar(object):  # 临时变量类，t1,t2……
    def __init__(self, name, cat="temp"):
        self.name = name
        self.cat = cat
        self._type = None

    def __str__(self):
        return "%s" % self.name


# 四元式类，存储自定义变量和临时变量都是存储相应类
class MiddleCode(object):

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


class Stack(object):  # 自定义栈
    def __init__(self):
        self.stack = list()

    def push1(self, item):
        self.stack.append(item)

    def pop1(self):
        if self.size() > 0:
            return self.stack.pop()
        else:
            print("Empty stack!")

    def size(self):
        return len(self.stack)


class Recursion(object):
    def __init__(self):
        self.cifa = CiFa(ALL_STARTSTATUS, ALL_STATUS, ALL_DERVEDICT,
                         ALL_ENDSTATUS, 'v.cpp')
        self.curToken = None
        self.testStack = []
        self.SEMStack = Stack()  # 语义分析栈，存储各种标识符和临时变量
        self.midCodeRes = list()  # 存储四元式的栈
        self.count = 1
        self.whether_in_param = 0  # 判断是否进入了参数列表，进入了设为1
        self.param_sem_stack = Stack()
    def getRes(self):
        return self.midCodeRes

    def token_to_word(self):
        if isinstance(self.curToken[1], int):
            return self.cifa.symbolList[self.curToken[0]][self.curToken[1]]
        elif isinstance(self.curToken[1], SymbolItem):
            return self.curToken[1].name

    def get_next_token(self, identAssign=True):
        self.curToken = self.cifa.get_next_token(identAssign)
        if self.curToken is False:
            # 文件读完,没有下一个token了
            self.error()
        self.testStack.append(self.token_to_word())
        if isinstance(self.curToken[1], SymbolItem):
            self.cifa.SL.activeSL.activeItem = self.curToken[1]

    # 错误
    def error(self):
        print('error')
        exit(0)

    #判断函数
    def jud_fun(self):
        if isinstance(self.curToken[1], SymbolItem):
            if self.curToken[1].cat == 'f':
                return True
        return False

    #不是函数
    def jud_nfun(self):
        if isinstance(self.curToken[1], SymbolItem):
            if self.curToken[1].cat != 'f':
                return True
        return False

    #标识符 ，（函数+非函数  ）,仅在声明时使用
    def jud_ident(self):
        if isinstance(self.curToken[1], SymbolItem):
            return True
        return False

    def jud_type(self):
        type_lis = ['int', 'bool', 'char', 'float']
        # 非标识符
        if isinstance(self.curToken[1], int):
            if self.cifa.symbolList[self.curToken[0]][self.
                                                      curToken[1]] in type_lis:
                return True
        return False

    #常数
    def jud_const(self):
        return self.curToken[0] == 'c'

    # TODO def PUSH
    def PUSH(self):
        if (isinstance(self.curToken[1], SymbolItem)):
            self.SEMStack.push1(self.curToken[1])
        else:
            self.SEMStack.push1(self.token_to_word())
        # print(self.SEMStack.len,"in PUSH")

    # def PUSH1(self):
    #     if(isinstance(self.curToken[1], SymbolItem)):
    #         self.param_sem_stack.push1(self.curToken[1])
    #     else:
    #         self.param_sem_stack.push1(self.token_to_word())

    def GEQ1Calculator(self, cal):  # 加减乘除四元式生成
        # if(self.whether_in_param == 1):
        #     item1 = self.param_sem_stack.pop1()
        #     item2 = self.param_sem_stack.pop1()
        #     result = "t" + str(self.count)
        #     self.count += 1
        #     temp_var = TempVar(result)
        #     quaternion = MiddleCode(cal, item2, item1, temp_var)
        #     self.midCodeRes.append(quaternion)
        #     self.param_sem_stack.push1(temp_var)
        # else:
        #     item1 = self.SEMStack.pop1()
        #     item2 = self.SEMStack.pop1()
        #     result = "t" + str(self.count)
        #     self.count += 1
        #     temp_var = TempVar(result)
        #     quaternion = MiddleCode(cal, item2, item1, temp_var)
        #     self.midCodeRes.append(quaternion)
        #     self.SEMStack.push1(temp_var)
        item1 = self.SEMStack.pop1()
        item2 = self.SEMStack.pop1()
        result = "t" + str(self.count)
        self.count += 1
        temp_var = TempVar(result)
        quaternion = MiddleCode(cal, item2, item1, temp_var)
        self.midCodeRes.append(quaternion)
        self.SEMStack.push1(temp_var)


    def GEQ2Assignment(self, cal):  # = 的四元式生成
        item1 = self.SEMStack.pop1()
        item2 = self.SEMStack.pop1()
        quaternion = MiddleCode(cal, item1, None, item2)
        self.midCodeRes.append(quaternion)

    def GEQEP(self):  # end of program四元式
        quaternion = MiddleCode("pe", None, None, None)
        self.midCodeRes.append(quaternion)

    def GEQ4pro(self):  # produce function
        item1 = self.SEMStack.pop1()
        quaternion = MiddleCode("pro", item1, None, None)
        self.midCodeRes.append(quaternion)

    def GEQ5if(self):  # if的四元式
        item1 = self.SEMStack.pop1()
        quaternion = MiddleCode("if", item1, None, None)
        self.midCodeRes.append(quaternion)

    def geq_end_if(self):
        quaternion = MiddleCode("ie", None, None, None)
        self.midCodeRes.append(quaternion)

    def GEQ6while(self):  # WHILE的四元式
        quaternion = MiddleCode("wh", None, None, None)
        self.midCodeRes.append(quaternion)

    def geq_end_while(self):
        quaternion = MiddleCode("we", None, None, None)
        self.midCodeRes.append(quaternion)

    def geq_else(self):  # else 四元式生成
        quaternion = MiddleCode("el", None, None, None)
        self.midCodeRes.append(quaternion)

    def geq_logical(self, cal):  # 逻辑表达式四元式生成
        item1 = self.SEMStack.pop1()
        item2 = self.SEMStack.pop1()
        result = "t" + str(self.count)
        self.count += 1
        temp_var = TempVar(result)
        quaternion = MiddleCode(cal, item2, item1, temp_var)
        self.midCodeRes.append(quaternion)
        self.SEMStack.push1(temp_var)

    def geq_do(self):  # do四元式生成
        item1 = self.SEMStack.pop1()
        quaternion = MiddleCode("do", item1, None, None)
        self.midCodeRes.append(quaternion)

    def GEQreturn(self):  # return的四元式
        item1 = self.SEMStack.pop1()
        quaternion = MiddleCode("ret", item1, None, None)
        self.midCodeRes.append(quaternion)

    def geq_without_init(self):  # 有定义但没设初值的自定义变量，赋初值0并生成四元式
        item1 = self.SEMStack.pop1()
        quaternion = MiddleCode("=", 0, None, item1)
        self.midCodeRes.append(quaternion)

    def geq_transmitted_param(self):  # 被传递的参数四元式生成
        # ass_param_sem_stack = Stack()
        # while self.param_sem_stack.size() > 0:
        #     ass_param_sem_stack.push1(self.param_sem_stack.pop1())
        # while ass_param_sem_stack.size() > 0:
        #     param = ass_param_sem_stack.pop1()
        #     quaternion = MiddleCode("param", param, None, None)
        #     self.midCodeRes.append(quaternion)
        #     # while self.param_sem_stack.size() > 0:
        #     #     param = self.param_sem_stack.pop1()
        #     #     quaternion = MiddleCode("param", param, None, None)
        #     #     self.midCodeRes.append(quaternion)
        item1 = self.SEMStack.pop1()
        mid_code = MiddleCode("param", item1, None, None)
        self.midCodeRes.append(mid_code)

    def geq_call_function(self, function):  #
        result = "t" + str(self.count)
        self.count += 1
        temp_var = TempVar(result)
        quaternion = MiddleCode("call", function, None, temp_var)
        self.midCodeRes.append(quaternion)
        self.SEMStack.push1(temp_var)

        # 主函数，解析，递归下降
    def parser(self):
        self.get_next_token()
        self.source_program()
        if self.token_to_word() != '#':
            print('error  缺少终结符#')
            exit(0)
        else:
            print('done')

    # 源程序
    def source_program(self):
        # <源程序> -> <类型><标识符><是否函数><源程序>
        if self.jud_type():  #如果是类型定义
            # 1
            self.cifa.SL.activeSL.curVarType = self.token_to_word()

            self.get_next_token(identAssign=False)
            if self.jud_ident():

                # TODO   PUSH
                self.PUSH()  #标识符压进SEMStack

                self.get_next_token()

                self.whether_function()

                self.source_program()
                return
            else:
                self.error()
        else:
            return

    # 是否函数
    def whether_function(self):
        # <是否函数>->(<形参列表>){<语句列表>}
        if (self.token_to_word() == '('):
            # TODO GEQ(produce function)
            self.GEQ4pro()
            self.cifa.SL.activeSL.curVarCat = 'f'
            self.cifa.SL.activeSL.fill_info_and_push_list()
            self.cifa.SL.create_next_level()

            self.get_next_token()
            self.form_list()
            # 9
            self.cifa.SL.fill_param_in_funclist()

            if (self.token_to_word() == ')'):
                self.get_next_token()
                if (self.token_to_word() == '{'):
                    self.get_next_token()
                    self.statement_list()
                    if (self.token_to_word() == '}'):
                        # TODO GEQ(end of program)
                        self.GEQEP()
                        self.cifa.SL.destory_next_level()

                        self.get_next_token()
                        return
                    else:
                        self.error()
                else:
                    self.error()
            else:
                self.error()
        # <变量列表><赋值语句>
        else:
            # 8
            self.cifa.SL.activeSL.fill_info_and_push_list()

            self.variable_list()
            self.assignment_statement()
            return

    # 形参列表
    def form_list(self):
        # <形参列表>-><类型><标识符><形参列表>
        if self.jud_type():
            # 7
            self.cifa.SL.activeSL.curVarCat = 'vn'
            self.cifa.SL.activeSL.curVarType = self.token_to_word()

            self.get_next_token(identAssign=False)
            if (self.jud_ident()):
                # 8
                self.cifa.SL.activeSL.fill_info_and_push_list()

                self.get_next_token()
                self.form_list()
                return
            else:
                self.error()
        # ,<形参列表>
        elif (self.token_to_word() == ','):
            self.get_next_token()
            self.form_list()
            return
        else:
            return

    # 语句列表
    def statement_list(self):
        #函数
        if self.jud_fun():
            # todo  GEQ(),call a function
            function_name = self.token_to_word()
            function_obj = self.curToken[1]
            self.get_next_token()
            if (self.token_to_word() == '('):

                self.get_next_token()
                self.with_or_without_parameters_1()
                self.geq_call_function(function_obj)

                if (self.token_to_word() == ';'):
                    self.get_next_token()
                    self.statement_list()

                else:
                    self.error()


                return

            else:
                self.error()
        #非函数
        elif (self.jud_nfun()):
            # todo PUSH(非函数标识符)
            self.PUSH()
            self.get_next_token()
            if (self.token_to_word() == '='):
                self.get_next_token()
                self.operation_expression()
                # TODO GEQ(=)
                self.GEQ2Assignment("=")
                if (self.token_to_word() == ';'):
                    self.get_next_token()
                    self.statement_list()
                    return
                else:
                    self.error()
            else:
                self.error()

        #return
        elif (self.token_to_word() == 'return'):
            self.get_next_token()
            self.operation_expression()
            # TODO GEQ(return)
            self.GEQreturn()
            if (self.token_to_word() == ';'):
                self.get_next_token()
                self.statement_list()
                return
            else:
                self.error()

        #<类型><标识符><变量列表><赋值语句><语句列表>
        elif (self.jud_type()):
            # 1
            self.cifa.SL.activeSL.curVarType = self.token_to_word()
            self.cifa.SL.activeSL.curVarCat = 'v'

            self.get_next_token(identAssign=False)

            if (self.jud_ident()):
                # TODO PUSH(标识符)
                self.PUSH()

                self.cifa.SL.activeSL.fill_info_and_push_list()
                self.get_next_token()
                self.variable_list()
                self.assignment_statement()
                self.statement_list()
                return
            else:
                self.error()
        #  if (< 运算表达式 > < 逻辑运算符 > < 运算表达式 >) {4 < 语句列表 >}5 < 有无else >
        elif (self.token_to_word() == 'if'):
            self.get_next_token()
            if (self.token_to_word() == '('):
                self.get_next_token()
                self.operation_expression()
                cal = self.token_to_word()
                self.logical_operator()
                self.operation_expression()
                # TODO GEQ(逻辑运算符)
                self.geq_logical(cal)
                if (self.token_to_word() == ')'):
                    # TODO GEQ(if)
                    self.GEQ5if()
                    self.get_next_token()
                    if (self.token_to_word() == '{'):
                        # 4
                        self.cifa.SL.create_next_level()

                        self.get_next_token()
                        self.statement_list()
                        if (self.token_to_word() == '}'):
                            # 5
                            self.cifa.SL.destory_next_level()

                            self.get_next_token()
                            self.with_or_without_else()

                            # TODO TEST
                            self.statement_list()

                            return
                        else:
                            self.error()
                    else:
                        self.error()
                else:
                    self.error()
            else:
                self.error()
        # while (< 运算表达式 > < 逻辑运算符 > < 运算表达式 >) {4 < 语句列表 >}5
        elif (self.token_to_word() == 'while'):
            # TODO GEQ(while)
            self.GEQ6while()
            self.get_next_token()
            if (self.token_to_word() == '('):
                self.get_next_token()
                self.operation_expression()
                cal = self.token_to_word()
                self.logical_operator()
                self.operation_expression()
                # TODO GEQ(逻辑运算符)
                self.geq_logical(cal)
                self.geq_do()
                if (self.token_to_word() == ')'):
                    self.get_next_token()
                    if (self.token_to_word() == '{'):
                        # 4
                        self.cifa.SL.create_next_level()

                        self.get_next_token()
                        self.statement_list()
                        if (self.token_to_word() == '}'):
                            # 5
                            self.geq_end_while()
                            self.cifa.SL.destory_next_level()

                            self.get_next_token()

                            # TODO TEST
                            self.statement_list()

                            return
                        else:
                            self.error()
                    else:
                        self.error()
                else:
                    self.error()
            else:
                self.error()
        else:
            return

    # # 有无参数
    # def with_or_without_parameters(self):
    #     if (self.token_to_word() == ')'):
    #         self.get_next_token()
    #         self.end_of_statement()
    #         return
    #     else:
    #         self.whether_in_param = 1
    #         self.operation_expression()
    #         self.variable_list()
    #         if (self.token_to_word() == ')'):
    #             self.geq_transmitted_param()
    #             self.whether_in_param = 0
    #             self.get_next_token()
    #             self.end_of_statement()
    #             return
    #         else:
    #             self.error()

    #语句结尾
    def end_of_statement(self):
        if (self.token_to_word() == ';'):
            self.get_next_token()
            self.statement_list()
            return
        else:
            self.error()

    def logical_operator(self):
        log_lis = ['>', '<', '==', '>=', '<=']
        if (self.token_to_word() in log_lis):
            self.get_next_token()
            return
        else:
            self.error()

    #有无else
    def with_or_without_else(self):
        if (self.token_to_word() == 'else'):
            # todo GEQ(else)
            self.geq_else()
            self.get_next_token()
            if (self.token_to_word() == '{'):
                # 4
                self.cifa.SL.create_next_level()

                self.get_next_token()
                self.statement_list()
                if (self.token_to_word() == '}'):
                    # 5
                    # TODO
                    self.geq_end_if()
                    self.cifa.SL.destory_next_level()

                    self.get_next_token()
                    return
                else:
                    self.error()
            else:
                self.error()
        else:
            self.geq_end_if()
            return

    #变量列表
    def variable_list(self):
        if (self.token_to_word() == ','):
            # TODO  GEQ(标识符),有定义但没设初值的变量，设初值0，（=，0，_,x)
            self.geq_without_init()
            self.get_next_token(identAssign=False)
            if (self.jud_ident()):
                # todo  PUSH()
                self.PUSH()
                self.cifa.SL.activeSL.fill_info_and_push_list()

                self.get_next_token()
                self.variable_list()
                return
            else:
                self.error()
        else:
            return

    #赋值语句
    def assignment_statement(self):
        if (self.token_to_word() == '='):

            self.get_next_token()
            self.operation_expression()

            # TODO GEQ()
            self.GEQ2Assignment("=")

            if (self.token_to_word() == ';'):
                self.get_next_token()
                return
            else:
                self.error()
        elif (self.token_to_word() == ';'):
            self.geq_without_init()
            self.get_next_token()
            return
        else:
            self.error()

    #运算表达式 ori
    def operation_expression(self):
        self.item()
        self.operation_expression_()
        return

    #项
    def item(self):
        self.factor()
        self.item_()
        return

    #表达式
    def operation_expression_(self):
        if (self.token_to_word() in ['+', '-']):
            cal = self.token_to_word()
            self.get_next_token()
            self.item()
            #TODO GEQ(+/-)
            self.GEQ1Calculator(cal)
            self.operation_expression_()
            return
        else:
            return

    #项_
    def item_(self):
        if (self.token_to_word() in ['*', '/']):
            cal = self.token_to_word()
            self.get_next_token()
            self.factor()
            self.GEQ1Calculator(cal)
            self.item_()
            return
        else:
            return

    #因子
    def factor(self):
        if (self.token_to_word() == '('):
            self.get_next_token()
            self.operation_expression()
            if (self.token_to_word() == ')'):
                self.get_next_token()
                return
            else:
                self.error()
        else:
            self.operation_object()
            return

    def operation_object(self):
        if (self.jud_fun()):
            # TODO  GEQ(call function)
            function_name = self.token_to_word()
            function_obj = self.curToken[1]
            self.get_next_token()
            if (self.token_to_word() == '('):
                self.get_next_token()
                self.with_or_without_parameters_1()
                self.geq_call_function(function_obj)
                return
            else:
                self.error()
        elif (self.jud_nfun()):
            # todo PUSH()
            # self.PUSH()
            # if self.whether_in_param == 1:
            #     self.PUSH1()
            # else:
            #     self.PUSH()
            self.PUSH()
            self.get_next_token()
            return
        elif (self.jud_const()):


            # self.PUSH()
            # if self.whether_in_param == 1:
            #     self.PUSH1()
            # else:
            #     self.PUSH()
            self.PUSH()
            self.get_next_token()
            return

        else:
            self.error()

    def with_or_without_parameters_1(self):
        if self.token_to_word() == ')':
            self.get_next_token()
            return
        else:
            self.whether_in_param = 1
            self.operation_expression()

            self.geq_transmitted_param()

            self.with_or_without_parameters_2()
            if self.token_to_word() == ')':
                # self.geq_transmitted_param()
                self.whether_in_param = 0
                self.get_next_token()
                return
            else:
                self.error()

    def with_or_without_parameters_2(self):
        if self.token_to_word() == ',':
            self.get_next_token()
            self.operation_expression()

            self.geq_transmitted_param()

            self.with_or_without_parameters_2()
            return
        else:
            return


if __name__ == "__main__":
    a = Recursion()
    a.parser()
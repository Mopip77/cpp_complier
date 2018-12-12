from cifa import CiFa
from config import *
from symbolList import SymbolItem

class Recursion(object):
    def __init__(self):
        self.cifa = CiFa(ALL_STARTSTATUS, ALL_STATUS, ALL_DERVEDICT, ALL_ENDSTATUS,
              'v.cpp')
        self.curToken = None
        self.testStack = []

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

    # 主函数，解析，递归下降
    def parser(self):
        self.get_next_token()
        self.source_program()
        if self.token_to_word() != '#':
            print('error  缺少终结符#')
            exit(0)
        else:
            print('done')

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
        type_lis=['int','bool','char','float']
        # 非标识符
        if isinstance(self.curToken[1], int):
            if self.cifa.symbolList[self.curToken[0]][self.curToken[1]] in type_lis:
                return True
        return False
    #常数
    def jud_const(self):
        return self.curToken[0] == 'c'

    # 源程序
    def source_program(self):
        # <源程序> -> <类型><标识符><是否函数><源程序>
        if self.jud_type():
            # 1
            self.cifa.SL.activeSL.curVarType = self.token_to_word()

            self.get_next_token(identAssign=False)
            if self.jud_ident():

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
        if(self.token_to_word() == '('):
            # 3
            self.cifa.SL.activeSL.curVarCat = 'f'
            self.cifa.SL.activeSL.fill_info_and_push_list()
            self.cifa.SL.create_next_level()

            self.get_next_token()
            self.form_list()
            # 9
            self.cifa.SL.fill_param_in_funclist()

            if(self.token_to_word() == ')'):
                self.get_next_token()
                if(self.token_to_word() == '{'):
                    self.get_next_token()
                    self.statement_list()
                    if(self.token_to_word() == '}'):
                        # 5
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
            if(self.jud_ident()):
                # 8
                self.cifa.SL.activeSL.fill_info_and_push_list()

                self.get_next_token()
                self.form_list()
                return
            else:
                self.error()
        # ,<形参列表>
        elif(self.token_to_word() == ','):
            self.get_next_token()
            self.form_list()
            return
        else:
            return

    # 语句列表
    def statement_list(self):
        #函数
        if self.jud_fun():
            self.get_next_token()
            if(self.token_to_word() == '('):
                self.get_next_token()
                self.with_or_without_parameters()
                return

            else:
               self.error()
        #非函数
        elif(self.jud_nfun()):
            self.get_next_token()
            if(self.token_to_word()=='='):
                self.get_next_token()
                self.operation_expression()
                if(self.token_to_word()==';'):
                    self.get_next_token()
                    self.statement_list()
                    return
                else:
                    self.error()
            else:
                self.error()

        #return
        elif(self.token_to_word()=='return'):
            self.get_next_token()
            self.operation_expression()
            if(self.token_to_word()==';'):
                self.get_next_token()
                self.statement_list()
                return
            else:
                self.error()

        #<类型><标识符><变量列表><赋值语句><语句列表>
        elif(self.jud_type()):
            # 1
            self.cifa.SL.activeSL.curVarType = self.token_to_word()

            self.get_next_token(identAssign=False)
            if(self.jud_ident()):
                # 8
                self.cifa.SL.activeSL.fill_info_and_push_list()

                self.get_next_token()
                self.variable_list()
                self.assignment_statement()
                self.statement_list()
                return
            else:
                self.error()

        elif(self.token_to_word()=='if'):
            self.get_next_token()
            if(self.token_to_word()=='('):
                self.get_next_token()
                self.operation_expression()
                self.logical_operator()
                self.operation_expression()
                if(self.token_to_word()==')'):
                    self.get_next_token()
                    if(self.token_to_word()=='{'):
                        # 4
                        self.cifa.SL.create_next_level()

                        self.get_next_token()
                        self.statement_list()
                        if(self.token_to_word()=='}'):
                            # 5
                            self.cifa.SL.destory_next_level()

                            self.get_next_token()
                            self.with_or_without_else()
                            return
                        else:
                            self.error()
                    else:
                        self.error()
                else:
                    self.error()
            else:
                self.error()

        elif(self.token_to_word()=='while'):
            self.get_next_token()
            if(self.token_to_word()=='('):
                self.get_next_token()
                self.operation_expression()
                self.logical_operator()
                self.operation_expression()
                if(self.token_to_word()==')'):
                    self.get_next_token()
                    if(self.token_to_word()=='{'):
                        # 4 
                        self.cifa.SL.create_next_level()

                        self.get_next_token()
                        self.statement_list()
                        if(self.token_to_word()=='}'):
                            # 5
                            self.cifa.SL.destory_next_level()

                            self.get_next_token()
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

    #有无参数
    def with_or_without_parameters(self):
        if(self.token_to_word()==')'):
            self.get_next_token()
            self.end_of_statement()
            return
        else:
            self.operation_expression()
            self.variable_list()
            if(self.token_to_word()==')'):
                self.get_next_token()
                self.end_of_statement()
                return
            else:
                self.error()


    #语句结尾
    def end_of_statement(self):
        if(self.token_to_word()==';'):
            self.get_next_token()
            self.statement_list()
            return
        else:
            self.error()


    def logical_operator(self):
        log_lis=['>','<','==','>=','<=']
        if(self.token_to_word() in log_lis):
            self.get_next_token()
            return
        else:
            self.error()


    #有无else
    def with_or_without_else(self):
        if(self.token_to_word()=='else'):
            self.get_next_token()
            if(self.token_to_word()=='{'):
                # 4
                self.cifa.SL.create_next_level()

                self.get_next_token()
                self.statement_list()
                if(self.token_to_word()=='}'):
                    # 5
                    self.cifa.SL.destory_next_level()

                    self.get_next_token()
                    return
                else:
                    self.error()
            else:
                self.error()
        else:
            return


    #变量列表
    def variable_list(self):
        if(self.token_to_word()==','):
            self.get_next_token(identAssign=False)
            if(self.jud_ident()):
                # 8
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
        if(self.token_to_word()=='='):
            self.get_next_token()
            self.operation_expression()
            if(self.token_to_word()==';'):
                self.get_next_token()
                return
            else:
                self.error()
        elif(self.token_to_word()==';'):
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
        if(self.token_to_word() in ['+','-']):
            self.get_next_token()
            self.item()
            self.operation_expression_()
            return
        else:
            return


    #项_
    def item_(self):
        if(self.token_to_word() in ['*','/']):
            self.get_next_token()
            self.factor()
            self.item_()
            return
        else:
            return

    #因子
    def factor(self):
        if(self.token_to_word()=='('):
            self.get_next_token()
            self.operation_expression()
            if(self.token_to_word()==')'):
                self.get_next_token()
                return
            else:
                self.error()
        else:
            self.operation_object()
            return


    def operation_object(self):
        if(self.jud_fun()):
            self.get_next_token()
            if(self.token_to_word()=='('):
                self.get_next_token()
                self.with_or_without_parameters_1()
                return
            else:
                self.error()
        elif(self.jud_nfun()):
            self.get_next_token()
            return
        elif(self.jud_const()):
            self.get_next_token()
            return

        else:
            self.error()

    def with_or_without_parameters_1(self):
        if self.token_to_word() == ')':
            self.get_next_token()
            return
        else:
            self.operation_expression()
            self.with_or_without_parameters_2()
            if self.token_to_word() == ')':
                self.get_next_token()
                return
            else:
                self.error()
    
    def with_or_without_parameters_2(self):
        if self.token_to_word() == ',':
            self.get_next_token()
            self.operation_expression()
            return
        else:
            return

if __name__ == "__main__":
    a = Recursion()
    a.parser()
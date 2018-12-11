class Recursion():

    word = ''  # 当前token

    def __init__(self):
        self.parser()

    # 读下一个token
    def next_word(self):
        pass

    # 错误
    def error(self):
        print('error')
        exit(0)

    # 主函数，解析，递归下降
    def parser(self):
        self.next_word()
        self.source_program()
        if self.word != '#':
            print('error  缺少终结符#')
            exit(0)
        else:
            print('done')

    #判断函数
    def jud_fun(self):
        pass
    #不是函数
    def jud_nfun(self):
        pass

    #标识符 ，（函数+非函数  ）
    def jud_ident(self):
        pass
    def jud_type():
        type_lis=['int','bool','char','float']
        if(self.word in type_lis):
            return 1
        else:
            return  0
    #常数
    def jud_const(self):
        pass


    # 源程序
    def source_program(self):
        # <源程序> -> <类型><标识符><是否函数><源程序>
        if(self.jud_type()):
            self.next_word()
            if(self.jud_ident()):
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
        if(self.word == '('):
            self.next_word()
            self.form_list()
            if(self.word == ')'):
                self.next_word()
                if(self.word == '{'):
                    self.next_word()
                    self.statement_list()
                    if(self.word == '}'):
                        self.next_word()
                        return
                    else:
                        self.error()
                else:
                    self.error()
            else:
                self.error()
        # <变量列表><赋值语句>
        else:
            self.variable_list()
            self.assignment_statement()
            return

    # 形参列表
    def form_list(self):
        # <形参列表>-><类型><标识符><形参列表>
        if(self.jud_type()):
            self.next_word()
            if(self.jud_ident()):
                self.next_word()
                self.form_list()
                return
            else:
                self.error()
        # ,<形参列表>
        elif(self.word == ','):
            self.next_word()
            self.form_list()
            return
        else:
            return

    # 语句列表
    def statement_list(self):
        #函数
        if(self.jud_fun()):
            self.next_word()
            if(self.word == '('):
                self.next_word()
                self.with_or_without_parameters()
                return

            else:
               self.error()
        #非函数
        elif(self.jud_nfun()):
            self.next_word()
            if(self.word=='='):
                self.next_word()
                self.operation_expression()
                if(self.word==';'):
                    self.next_word()
                    self.statement_list()
                    return
                else:
                    self.error()
            else:
                self.error()

        #return
        elif(self.word=='return'):
            self.next_word()
            self.operation_expression()
            if(self.word==';'):
                self.next_word()
                self.statement_list()
                return
            else:
                self.error()

        #<类型><标识符><变量列表><赋值语句><语句列表>
        elif(self.jud_type()):
            self.next_word()
            if(self.jud_ident()):
                self.next_word()
                self.variable_list()
                self.assignment_statement()
                self.statement_list()
                return
            else:
                self.error()

        elif(self.word=='if'):
            self.next_word()
            if(self.word=='('):
                self.next_word()
                self.operation_expression()
                self.logical_operator()
                self.operation_expression()
                if(self.word==')'):
                    self.next_word()
                    if(self.word=='{'):
                        self.next_word()
                        self.statement_list()
                        if(self.word=='}'):
                            self.next_word()
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

        elif(self.word=='while'):
            self.next_word()
            if(self.word=='('):
                self.next_word()
                self.operation_expression()
                self.logical_operator()
                self.operation_expression()
                if(self.word==')'):
                    self.next_word()
                    if(self.word=='{'):
                        self.next_word()
                        self.statement_list()
                        if(self.word=='}'):
                            self.next_word()
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
        if(self.word==')'):
            self.next_word()
            self.end_of_statement()
            return
        else:
            self.operation_expression()
            self.variable_list()
            if(self.word==')'):
                self.end_of_statement()
                return
            else:
                self.error()


    #语句结尾
    def end_of_statement(self):
        if(self.word==';'):
            self.next_word()
            self.statement_list()
            return
        else:
            self.error()


    def logical_operator(self):
        log_lis=['>','<','==','>=','<=']
        if(self.word in log_lis):
            self.next_word()
            return
        else:
            self.error()


    #有无else
    def with_or_without_else(self):
        if(self.word=='else'):
            self.next_word()
            if(self.word=='{'):
                self.next_word()
                self.statement_list()
                if(self.word=='}'):
                    self.next_word()
                    return
                else:
                    self.error()
            else:
                self.error()
        else:
            return


    #变量列表
    def variable_list(self):
        if(self.word==','):
            self.next_word()
            if(self.jud_ident()):
                self.variable_list()
                return
            else:
                self.error()
        else:
            return



    #赋值语句
    def assignment_statement(self):
        if(self.word=='='):
            self.next_word()
            self.operation_expression()
            if(self.word==';'):
                self.next_word()
                return
            else:
                self.error()
        elif(self.word==';'):
            self.next_word()
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
        if(self.word in ['+','-']):
            self.next_word()
            self.item()
            self.operation_expression_()
            return
        else:
            return


    #项_
    def item_(self):
        if(self.word in ['*','/']):
            self.next_word()
            self.factor()
            self.item_()
            return
        else:
            return

    #因子
    def factor(self):
        if(self.word=='('):
            self.next_word()
            self.operation_expression()
            if(self.word==')'):
                self.next_word()
                return
            else:
                self.error()
        else:
            self.operation_object()
            return


    def operation_object(self):
        if(self.jud_fun()):
            self.next_word()
            if(self.word=='('):
                self.next_word()
                self.with_or_without_parameters()
                return
            else:
                self.error()
        elif(self.jud_nfun()):
            self.next_word()
            return
        elif(self.jud_const()):
            self.next_word()
            return

        else:
            self.error()

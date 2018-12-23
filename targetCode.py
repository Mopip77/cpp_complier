from newdag import Optimizer
from Digui import MiddleCode
from Digui import SymbolItem
from Digui import MiddleCode
from Digui import TempVar
import Digui
from newdag import *
import re
print_code_block = """PR PROC NEAR
    MOV [DI],AX
    MOV DL,AH
    MOV BL,AH
    CALL SHOW
    MOV AX,[DI]
    MOV DL,AL
    MOV BL,AL
    CALL SHOW
    MOV AH,02H
    MOV DL,0AH
    INT 21H
RET
PR ENDP
SHOW PROC NEAR
    MOV CL,4
    SHR DL,CL
    CMP DL,10
    JAE FUHAO
    ADD DL,30H
    MOV AH,02H
    INT 21H
    JMP NEXT
FUHAO:
    ADD DL,37H
    MOV AH,02H
    INT 21H
NEXT:
    AND BL,0FH
    MOV DL,BL
    CMP BL,10
    JAE FUHAO2
    ADD DL,30H
    MOV AH,02H
    INT 21H
    JMP NEXT2
FUHAO2:
    ADD DL,37H
    MOV AH,2
    INT 21H
NEXT2:
    RET
SHOW ENDP"""

class Target_fun():
    j_w = ['_', '-', '+', '*', '/', '=', '>', '<', '>=', '<=', '==', 'ie', 'el', 'if', 'wh', 'do', 'we']

    def __init__(self):
        self.out_put_block = list()
        self.mid_codes = list()

        self.di_stack = list()
        self.di_stack.append(0)

        self.offset_dict_lis = list()
        new_dict = dict()
        self.offset_dict_lis.append(new_dict)

        self.fun_count = 0
        self.fun_count_lis = list()
        self.if_count = 0
        self.if_count_lis = list()
        self.wh_count = 0
        self.wh_count_lis = list()

    def run(self):
        code_head = """STACK SEGMENT STACK
DB 256 DUP(?)
STACK ENDS

DSEGM SEGMENT
DB 1000 DUP(?)
DSEGM ENDS

CSEGM SEGMENT
    ASSUME CS:CSEGM, DS:DSEGM, SS:STACK"""
        head_code2 = """PRO:
    MOV AX,DSEGM
    MOV DS,AX
    MOV AX,STACK
    MOV SS,AX"""
        self.out_put_block.append(code_head)
        self.out_put_block.append(print_code_block)
        self.out_put_block.append(head_code2)
        self.parse_block()
        self.out_put_block.append("CSEGM ENDS")
        self.out_put_block.append("    END PRO")

        here_num = 1
        length = len(self.out_put_block)
        for i in range(0, length):
            ret = re.search(r'(JNE|JLE|JGE|JL|JG) (.*)', self.out_put_block[i])
            if ret:
                if ret.group(1) == "JNE":
                    opposite = "JE"
                elif ret.group(1) == "JLE":
                    opposite = "JG"
                elif ret.group(1) == "JGE":
                    opposite = "JL"
                elif ret.group(1) == "JL":
                    opposite = "JGE"
                elif ret.group(1) == "JG":
                    opposite = "JLE"
                self.out_put_block[i] = "    %s HERE%s" % (opposite, here_num)
                self.out_put_block[i] += "\n"
                self.out_put_block[i] += "    JMP %s" % (ret.group(2))
                self.out_put_block[i] += "\n"
                self.out_put_block[i] += "HERE%s:" % here_num
                here_num += 1


    def load_mid_codes(self, mid_codes):
        self.mid_codes = mid_codes

    def entry(self):
        self.di_stack.append(0)
        new_dict = dict()
        self.offset_dict_lis.append(new_dict)

    def out(self):
        to_sub = self.di_stack.pop(-1)
        self.offset_dict_lis.pop(-1)
        self.offset_sub(to_sub)
        return to_sub

    def parse_block(self):
        now_is_global = 1
        cur_mc = 0
        for mc in self.mid_codes:
            cur_mc += 1
            if isinstance(mc, str):
                continue
            elif mc.opt == "pro":

                self.entry()

                self.fun_count += 1
                self.fun_count_lis.append(self.fun_count)
                if now_is_global == 1:
                    self.out_put_block.append("    CALL MAIN")
                    self.out_put_block.append("    MOV AH,4CH")
                    self.out_put_block.append("    INT 21H")
                    now_is_global = 0
                self.out_put_block.append("%s:" % mc.item1.name)
                self.out_put_block.append("    PUSH BP")
                self.out_put_block.append("    MOV BP,SP")
                param_num = mc.item1.addr.paramNum
                for i in range(0, param_num):
                    offset_of_param = 4 + (param_num - i - 1) * 2
                    self.out_put_block.append("    MOV DX,[BP+%s]" % str(offset_of_param))
                    self.out_put_block.append("    MOV [DI],DX")
                    self.out_put_block.append("    ADD DI,2")
                    param = mc.item1.addr.paramList[i]
                    self.offset_add(2)
                    self.offset_dict_lis[-1][param] = 2

            elif mc.opt == "ret":
                # ret a _ _
                if isinstance(mc.item1, int):
                    self.out_put_block.append("    MOV AX,%s" % str(mc.item1))
                elif isinstance(mc.item1, SymbolItem):
                    offset_of_a, is_define = self.find_offset(mc.item1)
                    self.out_put_block.append("    MOV AX,[DI-%s]" % str(offset_of_a))
                elif isinstance(mc.item1, tuple):
                    self.deal_arr_offset(mc.item1)
                    offset_of_a, is_define = self.find_offset(mc.item1[0])
                    self.out_put_block.append("    MOV AX,[DI+BX-%s]" % str(offset_of_a))
                self.out_put_block.append("    SUB DI,%s" % str(self.di_stack[-1]))
                self.di_stack[-1] = 0
                self.out_put_block.append("    JMP PE%s" % str(self.fun_count))

            elif mc.opt == "pe":

                self.out_put_block.append("PE%s:" % self.fun_count)

                to_sub = self.out()
                self.out_put_block.append("    SUB DI,%s" % str(to_sub))
                self.out_put_block.append("    POP BP")
                self.out_put_block.append("    RET")
                self.fun_count_lis.pop(-1)

            elif mc.opt == "=":  # = 1 _ a / = b _ a / = 0 _ arr / = 1 _ () / = b _ ()/ = () _ a
                if not isinstance(mc.res, tuple):
                    # TODO:如果支持char,这里需要改动
                    if (isinstance(mc.item1, int)):  # = 1 _ a
                        if mc.res.cat == "v":
                            offset_of_a, is_define = self.find_offset(mc.res)
                            self.out_put_block.append("    MOV DX,%s" % mc.item1)
                            self.out_put_block.append("    MOV [DI-%s],DX" % offset_of_a)
                            if is_define == 0:
                                self.out_put_block.append("    ADD DI,2")
                                self.offset_add(2)
                                self.offset_dict_lis[-1][mc.res] = 2

                        elif mc.res.cat == "arr":  # = 0 _ arr
                            length = mc.res.addr.len
                            if mc.res.type == "int":
                                type_length = 2
                            else:
                                # TODO:Char类型长度
                                type_length = 1
                            for i in range(0, length):
                                self.out_put_block.append("    MOV DX,0")
                                self.out_put_block.append("    MOV [DI],DX")
                                self.out_put_block.append("    ADD DI,%s" % str(type_length))
                                self.offset_add(type_length)
                            self.offset_dict_lis[-1][mc.res] = length * type_length

                    elif isinstance(mc.item1, SymbolItem):  # = b _ a
                        offset_of_b , is_define_b = self.find_offset(mc.item1)
                        offset_of_a, is_define = self.find_offset(mc.res)
                        self.out_put_block.append("    MOV DX,[DI-%s]" % str(offset_of_b))
                        self.out_put_block.append("    MOV [DI-%s],DX" % str(offset_of_a))
                        if is_define == 0:
                            self.out_put_block.append("    ADD DI,2")
                            self.offset_add(2)
                            self.offset_dict_lis[-1][mc.res] = 2

                    elif isinstance(mc.item1, tuple):  # = () _ a
                        offset_of_a, is_define_a = self.find_offset(mc.res)
                        offset_of_arr, is_define_arr = self.find_offset(mc.item1[0])
                        self.deal_arr_offset(mc.item1)
                        self.out_put_block.append("    MOV DX,[DI+BX-%s]" % offset_of_arr)
                        self.out_put_block.append("    MOV [DI-%s],DX" % offset_of_a)
                        if is_define_a == 0:
                            self.out_put_block.append("    ADD DI,2")
                            self.offset_add(2)
                            self.offset_dict_lis[-1][mc.res] = 2

                else:  # = 1 _ () / = b _ () / = () _ ()
                    # self.deal_arr_offset(mc.res)
                    # offset_of_a, is_define = self.find_offset(mc.res[0])
                    if isinstance(mc.item1, int):
                        self.deal_arr_offset(mc.res)
                        offset_of_a, is_define = self.find_offset(mc.res[0])
                        self.out_put_block.append("    MOV DX,%s" % str(mc.item1))
                        self.out_put_block.append("    MOV [DI+BX-%s],DX" % str(offset_of_a))
                    elif isinstance(mc.item1, SymbolItem):
                        self.deal_arr_offset(mc.res)
                        offset_of_a, is_define = self.find_offset(mc.res[0])
                        offset_of_b, is_define = self.find_offset(mc.item1)
                        self.out_put_block.append("    MOV DX,[DI-%s]" % str(offset_of_b))
                        self.out_put_block.append("    MOV [DI+BX-%s],DX" % str(offset_of_a))

                    elif isinstance(mc.item1, tuple): # = (a,?) _ (b,?)

                        offset_of_a, is_define = self.find_offset(mc.item1[0])
                        self.deal_arr_offset(mc.item1)
                        self.out_put_block.append("    MOV CX,[DI+BX-%s]" % offset_of_a)

                        offset_of_b, is_define = self.find_offset(mc.res[0])
                        self.deal_arr_offset(mc.res)
                        self.out_put_block.append("    MOV [DI+BX-%s],CX" % offset_of_b)


            elif mc.opt in ["+", "-", "*", "/"]:
                # + a b c / + a 1 c / + () 1 c
                # 取操作数1
                if isinstance(mc.item1, int):
                    self.out_put_block.append("    MOV AX,%s" % str(mc.item1))
                elif isinstance(mc.item1, SymbolItem):
                    offset_of_a ,is_define = self.find_offset(mc.item1)
                    self.out_put_block.append("    MOV AX,[DI-%s]" % str(offset_of_a))
                elif isinstance(mc.item1, tuple):
                    self.deal_arr_offset(mc.item1)
                    offset_of_a, is_define = self.find_offset(mc.item1[0])
                    self.out_put_block.append("    MOV AX,[DI+BX-%s]" % str(offset_of_a))

                # 取操作数2
                if isinstance(mc.item2, int):
                    self.out_put_block.append("    MOV BX,%s" % str(mc.item2))
                elif isinstance(mc.item2, SymbolItem):
                    offset_of_a, is_define = self.find_offset(mc.item2)
                    self.out_put_block.append("    MOV BX,[DI-%s]" % str(offset_of_a))
                elif isinstance(mc.item2, tuple):
                    self.out_put_block.append("    PUSH AX")
                    self.deal_arr_offset(mc.item2)
                    self.out_put_block.append("    POP AX")
                    offset_of_a, is_define = self.find_offset(mc.item2[0])
                    self.out_put_block.append("    MOV BX,[DI+BX-%s]" % str(offset_of_a))

                # 计算
                if mc.opt == "+":
                    self.out_put_block.append("    ADD AX,BX")
                elif mc.opt == "-":
                    self.out_put_block.append("    SUB AX,BX")
                elif mc.opt == "*":
                    self.out_put_block.append("    MUL BX")
                elif mc.opt == "/":
                    self.out_put_block.append("    DIV BX")
                # 把结果赋给res
                #self.out_put_block.append("    PUSH AX")
                if isinstance(mc.res, SymbolItem):
                    offset_of_res, is_define = self.find_offset(mc.res)
                    self.out_put_block.append("    MOV [DI-%s],AX" % str(offset_of_res))
                    if is_define == 0:
                        self.out_put_block.append("    ADD DI,2")
                        self.offset_add(2)
                        self.offset_dict_lis[-1][mc.res] = 2
                elif isinstance(mc.res, tuple):
                    self.out_put_block.append("    PUSH AX")
                    self.deal_arr_offset(mc.res)
                    self.out_put_block.append("    POP AX")
                    offset_of_a, is_define = self.find_offset(mc.res[0])
                    self.out_put_block.append("    MOV [DI+BX-%s],AX" % str(offset_of_a))

            elif mc.opt in [">", "<", ">=", "<=", "=="]:
                # 取第一个操作数
                if isinstance(mc.item1, int):
                    self.out_put_block.append("    MOV AX,%s" % str(mc.item1))
                elif isinstance(mc.item1, SymbolItem):
                    offset_of_a, is_define = self.find_offset(mc.item1)
                    self.out_put_block.append("    MOV AX,[DI-%s]" % str(offset_of_a))
                elif isinstance(mc.item1, tuple):
                    self.deal_arr_offset(mc.item1)
                    offset_of_a, is_define = self.find_offset(mc.item1[0])
                    self.out_put_block.append("    MOV AX,[DI+BX-%s]" % str(offset_of_a))
                # 取第二个操作数
                if isinstance(mc.item2, int):
                    self.out_put_block.append("    MOV BX,%s" % str(mc.item2))
                elif isinstance(mc.item2, SymbolItem):
                    offset_of_a, is_define = self.find_offset(mc.item2)
                    self.out_put_block.append("    MOV BX,[DI-%s]" % str(offset_of_a))
                elif isinstance(mc.item2, tuple):
                    self.out_put_block.append("    PUSH AX")
                    self.deal_arr_offset(mc.item2)
                    self.out_put_block.append("    POP AX")
                    offset_of_a, is_define = self.find_offset(mc.item2[0])
                    self.out_put_block.append("    MOV BX,[DI+BX-%s]" % str(offset_of_a))
                # 计算
                self.out_put_block.append("    SUB AX,BX")
                # 送结果
                if isinstance(mc.res, SymbolItem):
                    offset_of_res, is_define = self.find_offset(mc.res)
                    self.out_put_block.append("    MOV [DI-%s],AX" % str(offset_of_res))
                    if is_define == 0:
                        self.out_put_block.append("    ADD DI,2")
                        self.offset_add(2)
                        self.offset_dict_lis[-1][mc.res] = 2
                elif isinstance(mc.res, tuple):
                    self.out_put_block.append("    PUSH AX")
                    self.deal_arr_offset(mc.res)
                    self.out_put_block.append("    POP AX")
                    offset_of_a, is_define = self.find_offset(mc.res[0])
                    self.out_put_block.append("    MOV [DI+BX-%s],AX" % str(offset_of_a))

            elif mc.opt is "if":

                self.entry()

                self.if_count += 1
                self.if_count_lis.append(self.if_count)
                opt = self.mid_codes[cur_mc - 2].opt
                # 取操作数一
                if isinstance(mc.item1, int):
                    # self.out_put_block.append("    MOV AX,%s" % str(mc.item1))
                    if mc.item1 == 1:
                        self.out_put_block.append("IF%s:" % str(self.if_count))
                    elif mc.item1 == 0:
                        else_or_ie = self.find_down_for_if(cur_mc)
                        self.out_put_block.append("    JMP %s%s" % (else_or_ie, str(self.if_count)))
                        self.out_put_block.append("IF%s:" % str(self.if_count))
                    continue
                elif isinstance(mc.item1, SymbolItem):
                    offset_of_a, is_define = self.find_offset(mc.item1)
                    self.out_put_block.append("    MOV AX,[DI-%s]" % str(offset_of_a))
                elif isinstance(mc.item1, tuple):
                    self.deal_arr_offset(mc.item1)
                    offset_of_a, is_define = self.find_offset(mc.item1[0])
                    self.out_put_block.append("    MOV AX,[DI+BX-%s]" % str(offset_of_a))
                # 和0比较
                self.out_put_block.append("    CMP AX,0")
                # 判断跳else还是ie
                else_or_ie = self.find_down_for_if(cur_mc)
                # 判断opt
                if opt == "==":
                    self.out_put_block.append("    JNE %s%s" % (else_or_ie, str(self.if_count)))
                elif opt == ">":
                    self.out_put_block.append("    JLE %s%s" % (else_or_ie, str(self.if_count)))
                elif opt == "<":
                    self.out_put_block.append("    JGE %s%s" % (else_or_ie, str(self.if_count)))
                elif opt == ">=":
                    self.out_put_block.append("    JL %s%s" % (else_or_ie, str(self.if_count)))
                elif opt == "<=":
                    self.out_put_block.append("    JG %s%s" % (else_or_ie, str(self.if_count)))
                self.out_put_block.append("IF%s:" % str(self.if_count))

            elif mc.opt is "el":
                if_count = self.if_count_lis[-1]

                to_sub = self.out()
                self.out_put_block.append("    SUB DI,%s" % str(to_sub))

                self.out_put_block.append("    JMP IE%s" % if_count)
                self.out_put_block.append("ELSE%s:" % if_count)

                self.entry()

            elif mc.opt is "ie":
                if_count = self.if_count_lis[-1]

                to_sub = self.out()
                self.out_put_block.append("    SUB DI,%s" % str(to_sub))

                self.out_put_block.append("IE%s:" % if_count)
                self.if_count_lis.pop(-1)

            elif mc.opt is "wh":

                self.entry()

                self.wh_count += 1
                self.wh_count_lis.append(self.wh_count)
                self.out_put_block.append("WHILE%s:" % self.wh_count)

            elif mc.opt is "do":
                wh_count = self.wh_count_lis[-1]
                opt = self.mid_codes[cur_mc - 2].opt
                # 取操作数一
                if isinstance(mc.item1, int):
                    # self.out_put_block.append("    MOV AX,%s" % str(mc.item1))
                    if mc.item1 == 1:
                        self.out_put_block.append("DO%s:" % str(wh_count))

                        # to_sub = self.out()
                        # self.out_put_block.append("    SUB DI,%s" % str(to_sub))

                        self.entry()

                    elif mc.item1 == 0:
                        else_or_ie = self.find_down_for_if(cur_mc)
                        self.out_put_block.append("    JMP %s%s" % ("WE", str(wh_count)))
                        self.out_put_block.append("DO%s:" % str(wh_count))

                        # to_sub = self.out()
                        # self.out_put_block.append("    SUB DI,%s" % str(to_sub))

                        self.entry()

                    continue
                elif isinstance(mc.item1, SymbolItem):
                    offset_of_a, is_define = self.find_offset(mc.item1)
                    self.out_put_block.append("    MOV AX,[DI-%s]" % str(offset_of_a))
                elif isinstance(mc.item1, tuple):
                    self.deal_arr_offset(mc.item1)
                    offset_of_a, is_define = self.find_offset(mc.item1[0])
                    self.out_put_block.append("    MOV AX,[DI+BX-%s]" % str(offset_of_a))
                # 和0比较
                self.out_put_block.append("    CMP AX,0")
                if opt == "==":
                    self.out_put_block.append("    JNE %s%s" % ("WE", str(wh_count)))
                elif opt == ">":
                    self.out_put_block.append("    JLE %s%s" % ("WE", str(wh_count)))
                elif opt == "<":
                    self.out_put_block.append("    JGE %s%s" % ("WE", str(wh_count)))
                elif opt == ">=":
                    self.out_put_block.append("    JL %s%s" % ("WE", str(wh_count)))
                elif opt == "<=":
                    self.out_put_block.append("    JG %s%s" % ("WE", str(wh_count)))


                self.out_put_block.append("DO%s:" % str(wh_count))

                # to_sub = self.out()
                # self.out_put_block.append("    SUB DI,%s" % str(to_sub))

                self.entry()

            elif mc.opt is "we":
                wh_count = self.wh_count_lis[-1]
                self.wh_count_lis.pop(-1)

                to_sub = self.out()
                self.out_put_block.append("    SUB DI,%s" % str(to_sub))
                self.out_put_block.append("    SUB DI,%s" % str(self.di_stack[-1]))
                self.out_put_block.append("    JMP WHILE%s" % str(wh_count))

                self.out_put_block.append("WE%s:" % str(wh_count))

                to_sub = self.out()
                self.out_put_block.append("    SUB DI,%s" % str(to_sub))

            elif mc.opt is "param":
                # param _ _ 1
                if isinstance(mc.item1, int):
                    self.out_put_block.append("    MOV AX,%s" % mc.item1)
                    self.out_put_block.append("    PUSH AX")
                # param _ _ a
                elif isinstance(mc.item1, SymbolItem):
                    offset_of_a, is_define = self.find_offset(mc.item1)
                    self.out_put_block.append("    MOV AX,[DI-%s]" % str(offset_of_a))
                    self.out_put_block.append("    PUSH AX")
                # param _ _ ()
                elif isinstance(mc.item1, tuple):
                    self.deal_arr_offset(mc.item1)
                    offset_of_a, is_define = self.find_offset(mc.item1[0])
                    self.out_put_block.append("    MOV AX,[DI+BX-%s]" % str(offset_of_a))
                    self.out_put_block.append("    PUSH AX")
            elif mc.opt == "call":
                # call fun _ a/call fun _ ()
                if isinstance(mc.res, SymbolItem):
                    self.out_put_block.append("    CALL %s" % mc.item1.name)
                    offset_of_a, is_define = self.find_offset(mc.res)
                    self.out_put_block.append("    MOV [DI-%s],AX" % offset_of_a)
                    if is_define == 0:
                        self.out_put_block.append("    ADD DI,2")
                        self.offset_add(2)
                        self.offset_dict_lis[-1][mc.res] = 2
                    param_num = mc.item1.addr.paramNum
                    for i in range(0,param_num):
                        self.out_put_block.append("    POP DX")
                elif isinstance(mc.res, tuple):
                    self.out_put_block.append("    CALL %s" % mc.item1.name)
                    self.deal_arr_offset(mc.res)
                    offset_of_a, is_define = self.find_offset(mc.res[0])
                    self.out_put_block.append("    MOV [DI+BX-%s],AX" % str(offset_of_a))
                    param_num = mc.item1.addr.paramNum
                    for i in range(0, param_num):
                        self.out_put_block.append("    POP DX")
            elif mc.opt == "out":
                if isinstance(mc.res, int):
                    self.out_put_block.append("    MOV AX,%s" % str(mc.res))
                elif isinstance(mc.res, SymbolItem):
                    offset, is_define = self.find_offset(mc.res)
                    self.out_put_block.append("    MOV AX,[DI-%s]" % offset)
                elif isinstance(mc.res, tuple):
                    offset, is_define = self.find_offset(mc.res[0])
                    self.deal_arr_offset(mc.res)
                    self.out_put_block.append("    MOV AX,[DI+BX-%s]" % offset)
                self.out_put_block.append("    CALL PR")

    def find_down_for_if(self,cur_mc):
        flag = 0
        for mc in self.mid_codes[cur_mc:]:
            if mc == "":
                continue
            elif mc.opt == "if":
                flag += 1
            elif mc.opt == "el":
                if flag == 0:
                    return "ELSE"
            elif mc.opt == "ie":
                if flag == 0:
                    return "IE"
                flag -= 1

    def deal_arr_offset(self, item_of_tuple):
        type_length = 2
        if len(item_of_tuple) == 2:
            if isinstance(item_of_tuple[1], tuple):  # (a,(b,1))
                self.deal_arr_offset(item_of_tuple[1])
                # 把b[1]的值放到BX
                offset_of_b, is_define = self.find_offset(item_of_tuple[1][0])
                self.out_put_block.append("    MOV BX,[DI+BX-%s]" % str(offset_of_b))
                self.out_put_block.append("    MOV AX,%s" % str(type_length))
                self.out_put_block.append("    MUL BX")
                self.out_put_block.append("    MOV BX,AX")
            elif isinstance(item_of_tuple[1], SymbolItem):  # (a,b)
                offset_of_b, is_define = self.find_offset(item_of_tuple[1])
                self.out_put_block.append("    MOV BX,[DI-%s]" % str(offset_of_b))
                self.out_put_block.append("    MOV AX,%s" % str(type_length))
                self.out_put_block.append("    MUL BX")
                self.out_put_block.append("    MOV BX,AX")
            elif isinstance(item_of_tuple[1], int):
                self.out_put_block.append("    MOV BX,%s" % str(item_of_tuple[1]*type_length))
        elif len(item_of_tuple) >= 2: # (a,1,1) (a,2,b) (a,a(1,1),2)
            dimension = len(item_of_tuple) - 1
            self.out_put_block.append("    MOV CX,0")
            cur_index = 0
            for index in item_of_tuple[1:-1]:
                cur_index += 1
                if isinstance(index, int):
                    num = dimension - cur_index
                    offset = 1
                    for j in range(1, num+1):
                        offset *= item_of_tuple[0].addr.levelLenList[-j]
                    offset = offset * index
                    self.out_put_block.append("    MOV BX,%s" % str(offset))
                    self.out_put_block.append("    ADD CX,BX")
                elif isinstance(index, SymbolItem):
                    offset_of_b, is_define = self.find_offset(index)
                    num = dimension - cur_index
                    offset = 1
                    for j in range(1, num+1):
                        offset *= item_of_tuple[0].addr.levelLenList[-j]
                    self.out_put_block.append("    MOV BX,[DI-%s]" % str(offset_of_b))
                    self.out_put_block.append("    MOV AX,%s" % str(offset))
                    self.out_put_block.append("    MUL BX")
                    self.out_put_block.append("    MOV BX,AX")
                    self.out_put_block.append("    ADD CX,BX")
                elif isinstance(index, tuple):
                    num = dimension - cur_index
                    offset = 1
                    for j in range(1, num + 1):
                        offset *= item_of_tuple[0].addr.levelLenList[-j]

                    self.out_put_block.append("    PUSH CX")
                    self.deal_arr_offset(index)
                    offset_of_b, is_define = self.find_offset(index[0])
                    self.out_put_block.append("    MOV BX,[DI+BX-%s]" % str(offset_of_b))
                    self.out_put_block.append("    MOV AX,%s" % str(offset))
                    self.out_put_block.append("    MUL BX")
                    self.out_put_block.append("    MOV BX,AX")
                    self.out_put_block.append("    POP CX")
                    self.out_put_block.append("    ADD CX,BX")

            if isinstance(item_of_tuple[-1], int):
                self.out_put_block.append("    MOV BX,%s" % str(item_of_tuple[-1]))
                self.out_put_block.append("    ADD CX,BX")
            elif isinstance(item_of_tuple[-1], SymbolItem):
                offset_of_b, is_define = self.find_offset(item_of_tuple[-1])
                self.out_put_block.append("    MOV BX,[DI-%s]" % str(offset_of_b))
                self.out_put_block.append("    ADD CX,BX")
            elif isinstance(item_of_tuple[-1], tuple):
                offset_of_b, is_define = self.find_offset(index[0])
                self.out_put_block.append("    PUSH CX")
                self.deal_arr_offset(item_of_tuple[-1])
                self.out_put_block.append("    MOV BX,[DI+BX-%s]" % str(offset_of_b))
                self.out_put_block.append("    POP CX")
                self.out_put_block.append("    ADD CX,BX")
            self.out_put_block.append("    MOV BX,CX")
            self.out_put_block.append("    MOV AX,%s" % str(type_length))
            self.out_put_block.append("    MUL BX")
            self.out_put_block.append("    MOV BX,AX")


    def calculate_offset(self, item):
        if item.type == "int":
            return 2

    def find_offset(self, item):
        offset = 0
        is_define = 0
        for dict in self.offset_dict_lis[::-1]:
            try:
                offset = dict[item]
                is_define = 1
                return offset, is_define
            except:
                pass
        return offset, is_define

    def offset_add(self, offset):
        for dict in self.offset_dict_lis:
            for key in dict:
                dict[key] += offset
        self.di_stack[-1] += offset

    def offset_sub(self, offset):
        for dict in self.offset_dict_lis:
            for key in dict:
                dict[key] -= offset


if __name__ == '__main__':
    v = LR()
    with open("v.cpp", "r") as f:
        code = f.read()
    mid_codes = v.analyse(code)
    o = Optimizer()
    o.load_mid_codes(mid_codes)
    o.run()
    mid_codes = o.get_result()
    t = Target_fun()
    t.load_mid_codes(mid_codes)
    t.run()
    for l in t.out_put_block:
        print(l)
    with open("/home/bing/Masm/V.ASM", "w") as f:
        for l in t.out_put_block:
            f.write(l)
            f.write("\n")
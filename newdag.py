import Digui
from Digui import TempVar
from Digui import SymbolItem
from Digui import MiddleCode
from auto_dev import *


# class SymbolItem(object):
#     def __init__(self, name, _type, cat, addr):
#         self.name = name
#         self.type = _type
#         self.cat = cat
#         self.addr = addr
#
#     # for test
#     def __str__(self):
#         return "%s" % self.name

# class TempVar(object):  # 临时变量类，t1,t2……
#     def __init__(self, name, cat="temp"):
#         self.name = name
#         self.cat = cat
#
#     def __str__(self):
#         return "%s" % self.name


# class MiddleCode(object):
#
#     def __init__(self, opt, item1=None, item2=None, res=None):
#         self.opt = opt
#         self.item1 = item1
#         self.item2 = item2
#         self.res = res
#
#     # for test
#     def __str__(self):
#         if isinstance(self.item1, SymbolItem) or isinstance(self.item1, TempVar):
#             item1 = self.item1.name
#         else:
#             item1 = self.item1
#         if isinstance(self.item2, SymbolItem) or isinstance(self.item2, TempVar):
#             item2 = self.item2.name
#         else:
#             item2 = self.item2
#         if isinstance(self.res, SymbolItem) or isinstance(self.res, TempVar):
#             res = self.res.name
#         else:
#             res = self.res
#         return "%s %s %s %s" % (self.opt, item1, item2, res)


class DAG_Node(object):

    def __init__(self, number, opt, *args):
        self.number = number  # 节点编码
        self.opt = opt  # 节点的运算符
        self.marks = list(args)  # 节点的标记, 首元素为主标记, 后面为附加标记
        self.left_node = None
        self.right_node = None


class DAG(object):

    def __init__(self):
        self.node_list = list()
        self.exist = -1
        self.expr = -1

    def find(self, item):
        """
        逆序遍历当前节点,确定此项是否已经被定义过
        """
        for node in self.node_list[::-1]:
            if item in node.marks:
                self.exist = node.number
                return True
            else:
                pass
        return False

    def find_expr(self, opt, item1, item2):
        """
        遍历当前节点,确定此表达式是否已经被定义过
        """
        for node in self.node_list:
            if (node.opt == opt and
                    item1 in self.node_list[node.left_node].marks and
                    item2 in self.node_list[node.right_node].marks):
                self.expr = node.number
                return True
            else:
                pass
        return False

    def delete(self, item):
        """
        遍历符号表，找到除了本节点外所有附加标记中的此项
        """
        for node in self.node_list:
            # 防止主标记被删
            if item in node.marks[1:]:
                node.marks.remove(item)
            else:
                pass

    def deal_no_sys_item(self, number, item, res):
        """
        处理非符号表项类
        一般为一个数字或者一个字符
        :return:
        """
        # 若这个项已经在图中存在,则在此节点的标记中添加上res
        # 并删除除了本节点外，所有节点附加标志中的ａ
        if self.find(item):
            self.delete(res)
            self.node_list[self.exist].marks.append(res)

        # 如果不存在，则申请新节点
        else:
            self.delete(res)
            new_node = DAG_Node(number, "=", item, res)
            self.node_list.append(new_node)


class Optimizer(object):

    def __init__(self):
        self.mid_codes = list()  # 中间代码
        self.dag = DAG()
        self.result = list()

    def load_mid_codes(self, mid_codes):
        self.mid_codes = mid_codes

    def run(self):
        if self.block_codes() == False:
            print(self.result[0])  # for test
            return
        else:
            print("ok")

    def get_result(self):
        return self.result

    def block_codes(self):
        """
        处理分块并在块内部进行优化
        """
        low, high = 0, 0
        export_stat = ["if", "el", "ie", "wh", "do", "we", "pe", "pro", "ret"]
        nums = len(self.mid_codes)
        level = 0
        while high < nums:
            if self.mid_codes[high].opt in export_stat:
                if low <= high:
                    self.dag_born(low, high)
                    self.dag_to_res()
                    self.deal_temp_type()
                    self.result.append("")
                    self.dag.node_list.clear()
                    # if self.deal_param_overflow() == False:
                    #     self.result.clear()
                    #     self.result.append("Error:函数参数不匹配")
                    #     return False
                else:
                    pass
                high += 1
                low = high
            else:
                high += 1

    def deal_temp_type(self):
        maybe_temp_opts = ["+", "-", "*", "/", ">", "<", "==", ">=", "<=", "call"]
        for mc in self.result:
            if isinstance(mc, str):
                continue
            elif mc.opt in maybe_temp_opts:
                if isinstance(mc.res, TempVar):
                    type_ = self.judge_type(mc.item1, mc.item2, mc.opt)
                    new_res = SymbolItem(mc.res.name, type_, "v", None)
                    old_res = mc.res
                    mc.res = new_res
                    for mc2 in self.result:
                        if isinstance(mc2, str):
                            continue
                        if mc2.item1 == old_res:
                            mc2.item1 = new_res
                        else:
                            pass
                        if mc2.item2 == old_res:
                            mc2.item2 = new_res
                        else:
                            pass
                        if mc2.res == old_res:
                            mc2.res = new_res
                        else:
                            pass
                    for mc2 in self.result:
                        if isinstance(mc2, str):
                            continue
                        if isinstance(mc2.item1, tuple):
                            temp_list = list(mc2.item1)
                            tuple_length = len(temp_list)
                            for i in range(tuple_length):
                                if temp_list[i] == old_res:
                                    temp_list[i] = new_res
                            new_tuple = tuple(temp_list)
                            mc2.item1 = new_tuple
                        if isinstance(mc2.item2, tuple):
                            temp_list = list(mc2.item2)
                            tuple_length = len(temp_list)
                            for i in range(tuple_length):
                                if temp_list[i] == old_res:
                                    temp_list[i] = new_res
                            new_tuple = tuple(temp_list)
                            mc2.item2 = new_tuple
                        if isinstance(mc2.res, tuple):
                            temp_list = list(mc2.res)
                            tuple_length = len(temp_list)
                            for i in range(tuple_length):
                                if temp_list[i] == old_res:
                                    temp_list[i] = new_res
                            new_tuple = tuple(temp_list)
                            mc2.res = new_tuple

                else:
                    pass
            else:
                pass

    def judge_type(self, item1, item2, opt):
        if isinstance(item1, SymbolItem) and isinstance(item2, SymbolItem):
            if opt in [">", "<", "==", ">=", "<="]:
                return "int"
            elif item1.type == "int" and item2.type == "int":
                return "int"
        elif opt == "call":
            return item1.type

    def deal_param_overflow(self):
        param_num = 0
        for mc in self.result:
            if mc == "":
                continue
            elif mc.opt == "param":
                param_num += 1
            elif mc.opt == "call":
                if param_num != mc.item1.addr.paramNum:
                    return False
                else:
                    param_num = 0
            else:
                pass
        return True

    def calculation(self, item1, item2, opt, res):
        temp = item1 + item2 if opt == "+" else 0
        temp = item1 - item2 if opt == "-" else temp
        temp = item1 * item2 if opt == "*" else temp
        temp = item1 / item2 if opt == "/" else temp
        temp = item1 > item2 if opt == ">" else temp
        temp = item1 < item2 if opt == "<" else temp
        temp = item1 == item2 if opt == "==" else temp
        temp = item1 >= item2 if opt == ">=" else temp
        temp = item1 <= item2 if opt == "<=" else temp
        if isinstance(temp, bool):
            return int(temp)
        return temp
        # if opt == "+":
        #     return item1 + item2
        # elif opt == "-":
        #     return item1 - item2
        # elif opt == "*":
        #     return item1 * item2
        # elif opt == "/":
        #     return item1 / item2
        # else:
        #     return res

    def not_sy_item(self, item):
        if (isinstance(item, int) or
                isinstance(item, float) or
                isinstance(item, str)):
            return True
        else:
            return False

    def dag_born(self, low, high):
        opts = ["+", "-", "*", "/", ">", "<", "==", ">=", "<="]
        logic_opts = [">", "<", "==", ">=", "<="]
        sp_opts = ["if", "el", "ie", "wh", "do", "we", "pro", "ret", "pe", "param", "call","out"]

        # 生成图信息
        while low <= high:
            mc = self.mid_codes[low]
            low += 1
            number = len(self.dag.node_list)

            # TODO 如果需要加类型在此处加
            # 如果是赋值操作 即形如 (= 1 _ a) / (= b _ a)
            if mc.opt == "=":
                if self.not_sy_item(mc.item1):
                    self.dag.deal_no_sys_item(number, mc.item1, mc.res)
                else:
                    if isinstance(mc.item1, TempVar):
                        if self.dag.find(mc.item1):
                            self.dag.delete(mc.res)
                            self.dag.node_list[self.dag.exist].marks.append(mc.res)
                        else:
                            new_node = DAG_Node(number, "=", mc.item1, mc.res)
                            self.dag.delete(mc.res)
                            self.dag.node_list.append(new_node)
                    else:
                        new_node = DAG_Node(number, "=", mc.item1, mc.res)
                        self.dag.delete(mc.res)
                        self.dag.node_list.append(new_node)
            elif mc.opt in opts:
                if self.not_sy_item(mc.item1) and self.not_sy_item(mc.item2):
                    # TODO 在此处判断运算式两项是否符合运算规则
                    temp = self.calculation(mc.item1, mc.item2, mc.opt, mc.res)
                    self.dag.deal_no_sys_item(number, temp, mc.res)
                else:
                    # TODO 在此处判断运算式两项是否符合运算规则,如int+float之
                    # if self.dag.find_expr(mc.opt, mc.item1, mc.item2):
                    #     self.dag.delete(mc.res)
                    #     self.dag.node_list[self.dag.expr].marks.append(mc.res)
                    # else:
                    if self.dag.find(mc.item1):
                        left_node_number = self.dag.exist
                    else:
                        new_node = DAG_Node(number, "=", mc.item1)
                        self.dag.node_list.append(new_node)
                        left_node_number = number
                        number += 1

                    if self.dag.find(mc.item2):
                        right_node_number = self.dag.exist
                    else:
                        new_node = DAG_Node(number, "=", mc.item2)
                        self.dag.node_list.append(new_node)
                        right_node_number = number
                        number += 1

                    if (self.not_sy_item(self.dag.node_list[left_node_number].marks[0]) and
                            self.not_sy_item(self.dag.node_list[right_node_number].marks[0]) and
                            1):
                        # TODO 在此处判断运算式两项是否符合运算规则
                        temp = self.calculation(self.dag.node_list[left_node_number].marks[0],
                                                self.dag.node_list[right_node_number].marks[0], mc.opt, mc.res)
                        self.dag.deal_no_sys_item(number, temp, mc.res)
                    else:
                        new_node = DAG_Node(number, mc.opt, mc.res)
                        new_node.left_node = left_node_number
                        new_node.right_node = right_node_number
                        self.dag.node_list.append(new_node)
            elif mc.opt in sp_opts:
                if mc.opt in ["pro"]:
                    new_node = DAG_Node(number, mc.opt, mc.item1)
                    self.dag.node_list.append(new_node)
                elif mc.opt in ["call"]:
                    new_node = DAG_Node(number, "=", mc.item1)
                    self.dag.node_list.append(new_node)
                    number += 1
                    new_node = DAG_Node(number, mc.opt, mc.res)
                    new_node.left_node = number - 1
                    self.dag.node_list.append(new_node)
                elif mc.opt in ["if", "do", "ret", "param"]:
                    if self.dag.find(mc.item1):
                        left_node_number = self.dag.exist
                    else:
                        new_node = DAG_Node(number, "=", mc.item1)
                        self.dag.node_list.append(new_node)
                        left_node_number = number
                        number += 1
                    new_node = DAG_Node(number, mc.opt)
                    new_node.left_node = left_node_number
                    self.dag.node_list.append(new_node)
                elif mc.opt in ["el", "ie", "wh", "we", "pe"]:
                    new_node = DAG_Node(number, mc.opt)
                    self.dag.node_list.append(new_node)
                elif mc.opt == "out":
                    new_node = DAG_Node(number, mc.opt, mc.res)
                    self.dag.node_list.append(new_node)

        # 处理节点顺序
        # 非符号表项(数字 字符 小数) > 标识符　＞　形参 >　临时变量
        for node in self.dag.node_list:
            num = len(node.marks)

            # 无标记或只有一个标记　无须处理
            if num <= 1:
                continue
            else:
                for i in range(0, num):
                    if self.not_sy_item(node.marks[i]):
                        temp = node.marks.pop(i)
                        node.marks[1:] = node.marks[0:]
                        node.marks[0] = temp
                    else:
                        pass
                    if not isinstance(node.marks[i], TempVar):
                        for j in range(0, i):
                            if isinstance(node.marks[j], TempVar):
                                node.marks[i], node.marks[j] = node.marks[j], node.marks[i]
                                break
                            else:
                                pass
                    else:
                        pass
                for i in range(0, num):
                    if isinstance(node.marks[i], SymbolItem) or isinstance(node.marks[i], tuple):
                        if isinstance(node.marks[i], tuple) or node.marks[i].cat == "v":
                            for j in range(0, i):
                                if isinstance(node.marks[j], SymbolItem):
                                    if node.marks[j].cat == "vn":  # param
                                        node.marks[i], node.marks[j] = node.marks[j], node.marks[i]
                                        break
                                    else:
                                        pass
                                else:
                                    pass
                        else:
                            pass
                    else:
                        pass

    def dag_to_res(self):

        for node in self.dag.node_list:
            length_of_marks = len(node.marks)
            for j in range(length_of_marks):
                item = node.marks[j]
                if isinstance(item, tuple):
                    temp_list = list(item)
                    length = len(item)
                    for i in range(0, length):
                        if isinstance(temp_list[i],TempVar):
                            self.dag.find(temp_list[i])
                            new_index = self.dag.node_list[self.dag.exist].marks[0]
                            temp_list[i] = new_index
                        else:
                            pass
                    new_tuple = tuple(temp_list)
                    node.marks[j] = new_tuple

        for node in self.dag.node_list:
            if node.opt == "pro":
                mc = MiddleCode(node.opt, node.marks[0])
                self.result.append(mc)
            elif node.opt == "out":
                mc = MiddleCode(node.opt, None, None, node.marks[0])
                self.result.append(mc)
            elif node.opt in ["if", "do", "ret", "param"]:
                mc = MiddleCode(node.opt, self.dag.node_list[node.left_node].marks[0], None, None)
                self.result.append(mc)
            elif node.opt in ["el", "ie", "wh", "we", "pe"]:
                mc = MiddleCode(node.opt)
                self.result.append(mc)
            elif node.opt in ["call"]:
                mc = MiddleCode(node.opt, self.dag.node_list[node.left_node].marks[0], None, node.marks[0])
                self.result.append(mc)
                for m in node.marks[1:]:
                    if isinstance(m, tuple):
                        mc = MiddleCode("=", node.marks[0], None, m)
                        self.result.append(mc)
                    if not isinstance(m, TempVar) and not isinstance(m, tuple):
                        if m.cat == "vn":
                            mc = MiddleCode("=", m, None, node.marks[0])
                            self.result.append(mc)
                        else:
                            mc = MiddleCode("=", node.marks[0], None, m)
                            self.result.append(mc)
                    else:
                        pass
            elif node.opt == "=":
                for m in node.marks[1:]:
                    if isinstance(m, tuple):
                        mc = MiddleCode("=", node.marks[0], None, m)
                        self.result.append(mc)
                    if not isinstance(m, TempVar) and not isinstance(m, tuple):
                        if m.cat == "vn":
                            mc = MiddleCode("=", m, None, node.marks[0])
                            self.result.append(mc)
                        else:
                            mc = MiddleCode("=", node.marks[0], None, m)
                            self.result.append(mc)
                    else:
                        pass
            else:
                mc = MiddleCode(node.opt, self.dag.node_list[node.left_node].marks[0],
                                self.dag.node_list[node.right_node].marks[0], node.marks[0])
                self.result.append(mc)
                for m in node.marks[1:]:
                    if isinstance(m, tuple):
                        mc = MiddleCode("=", node.marks[0], None, m)
                        self.result.append(mc)
                    if not isinstance(m, TempVar) and not isinstance(m, tuple):
                        if m.cat == "vn":
                            mc = MiddleCode("=", m, None, node.marks[0])
                            self.result.append(mc)
                        else:
                            mc = MiddleCode("=", node.marks[0], None, m)
                            self.result.append(mc)
                    else:
                        pass


if __name__ == '__main__':
    v = LR()
    with open("v.cpp", "r") as f:
        code = f.read()
    mid_codes = v.analyse(code)
    o = Optimizer()
    o.load_mid_codes(mid_codes)
    o.run()
    for m in o.result:
        if m == "":
            continue
        print(m)

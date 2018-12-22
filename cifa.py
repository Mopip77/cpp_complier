from config import *
from fa import AllFA
from symbolList import SymbolListSystem, SymbolItem
from myerror import UnDefined

class CiFa(AllFA):
    log_path = 'result.txt'
    

    def __init__(self, startstatus, status, dervedict, endstatus, filename):
        checkingStr = self._load_content_from_file(filename) + ENDCHAR
        super(CiFa, self).__init__(startstatus, status, dervedict, endstatus,
                                   checkingStr)
        self.symbolList = {
            'C': [],  # 字符
            'S': [],  # 字符串
            'c': [],  # 常数
            'k': k_LIST,  # 关键字
            'p': p_LIST,  # 界符
            'end': [ENDCHAR], # 符号串结束
        }
        self.guiyueList = GUIYUE_LIST
        self.tokenList = []
        self.SL = SymbolListSystem()

    def _load_content_from_file(self, filename):
        with open(filename, 'r') as f:
            return f.read()

    def insert_file_content(self, filename):
        with open(filename, 'r') as f:
            fileContent = f.read()
        self.checkingStr = self.checkingStr[:self.curPos] + \
                                fileContent + \
                                self.checkingStr[self.curPos+1:]
        self.curPos -= 1
        self.strLen += len(fileContent)

    def add_to_symbol_list(self, Str):
        """
        将当前字符串加到表中，返回token
        identAssign 表示标识符是声明False还是赋值True
        """
        # 当前串的类型
        c = self.guiyueList[self.curStus]
        # 接受#, 结束状态
        if c == 'end':
            return ('end', 0)
        # 当前状态是2的时候可能是关键字
        if self.curStus == 2 and Str in self.symbolList['k']:
            return ('k', self.symbolList['k'].index(Str))
        # 其他非标识符类型
        if c != 'i':
            if Str not in self.symbolList[c]:
                self.symbolList[c].append(Str)
            return (c, self.symbolList[c].index(Str))
        else:
            si = self.SL.find(Str, 'all')
            if si is not False:
                return ('i', si)
            else:
                return ('i', SymbolItem(Str, None, None, None))

    def _save_token_to_file(self):
        with open(CiFa.log_path, 'w') as f:
            for token in self.tokenList:
                name = token[0]
                pos = token[1]
                if name == 'i':
                    f.write('{:<10}\n'.format(pos.name))
                else:
                    f.write('{:<10}{}\n'.format(self.symbolList[name][pos], token))

    def get_next_token(self):
        """
        返回下一个token串，若识别串读完则返回False,异常抛出到run函数去处理
        """
        if self.curPos > self.strLen:
            return False
        try:
            self.curStus = 1
            value = self.get_next_str()
            token = self.add_to_symbol_list(value)
            if token[0] == 'i':
                self.SL.activeSL.activeItem = token[1]
            return token
        except Exception as e:
            raise e

    def run(self):
        """
        运行词法检查
        """
        # 定义时也需要让其他继承该类的顺利初始化，此时是重置，比如连续两次调用run
        self.curChar = self.checkingStr[0]
        try:
            while True:
                token = self.get_next_token()
                # 文件读完
                if token is False:
                    break
                self.tokenList.append(token)
            print('[*]当前识别串属于该自动机的文法')
        except Exception as e:
            print(e)
        finally:
            self._save_token_to_file()


def main():
    CF = CiFa(ALL_STARTSTATUS, ALL_STATUS, ALL_DERVEDICT, ALL_ENDSTATUS,
              'v.cpp')
    try:
        CF.run()
    finally:
        print(2)


if __name__ == '__main__':
    main()

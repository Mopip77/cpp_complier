# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *
import re
import sys
from newdag import *
from targetCode import *
import os
import time
from config import WENFA_DICT
import threading



class MyLexer(QsciLexerCustom):

    def __init__(self, parent):
        super(MyLexer, self).__init__(parent)


        # Default text settings
        # ----------------------
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont("Consolas", 12))

        # Initialize colors per style
        # ----------------------------
        self.setColor(QColor("#ff000000"), 0)   # Style 0: black
        self.setColor(QColor("#ff7f0000"), 1)   # Style 1: red
        self.setColor(QColor("#ff0000bf"), 2)   # Style 2: blue
        self.setColor(QColor("#ff007f00"), 3)   # Style 3: green

        # Initialize paper colors per style
        # ----------------------------------
        self.setPaper(QColor("#ffffffff"), 0)   # Style 0: white
        self.setPaper(QColor("#ffffffff"), 1)   # Style 1: white
        self.setPaper(QColor("#ffffffff"), 2)   # Style 2: white
        self.setPaper(QColor("#ffffffff"), 3)   # Style 3: white

        # Initialize fonts per style
        # ---------------------------
        self.setFont(QFont("Consolas", 12), 0)   # Style 0: Consolas 14pt
        self.setFont(QFont("Consolas", 12), 1)   # Style 1: Consolas 14pt
        self.setFont(QFont("Consolas", 12), 2)   # Style 2: Consolas 14pt
        self.setFont(QFont("Consolas", 12), 3)   # Style 3: Consolas 14pt

    ''''''

    def language(self):
        return "SimpleLanguage"
    ''''''

    def description(self, style):
        if style == 0:
            return "myStyle_0"
        elif style == 1:
            return "myStyle_1"
        elif style == 2:
            return "myStyle_2"
        elif style == 3:
            return "myStyle_3"
        ###
        return ""
    ''''''

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.parent().text()[start:end]
        # p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")
        p = re.compile(r"\/\/|\n|\s+|\w+|\W")

        token_list = [ (token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]
        multiline_comm_flag = False
        editor = self.parent()
        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == 3:
                multiline_comm_flag = False
        # # multiline_comm_flag = False
        # if start > 0:
        #     multiline_comm_flag = False
        for i, token in enumerate(token_list):
            if multiline_comm_flag:
                self.setStyling(token[1], 3)
                if token[0] == "\n":
                    multiline_comm_flag = False
            else:
                if token[0] in ["for", "while", "return", "int", "include", "main", "print"]:
                    # Red style
                    self.setStyling(token[1], 1)

                elif token[0] in ["(", ")", "{", "}", "[", "]", "#"]:
                    # Blue style
                    self.setStyling(token[1], 2)

                elif token[0] == "//":
                    multiline_comm_flag = True
                    self.setStyling(token[1], 3)

                else:
                    # Default style
                    self.setStyling(token[1], 0)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.openfile_name = ""
        self.LRAnalysier = LR()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 900)

        qr = MainWindow.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        MainWindow.move(qr.topLeft())

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.textEdit = QsciScintilla()
        self.textEdit.setMarginType(0, QsciScintilla.NumberMargin)
        self.textEdit.setMarginWidth(0, "0000")
        self.textEdit.setMarginsForegroundColor(QColor("#ff888888"))
        # self.textEdit.setUtf8(True)
        self.__laxer = MyLexer(self.textEdit)
        self.textEdit.setLexer(self.__laxer)



        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(550, 0, 281, 531))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setFont(QFont("Consolas", 12))

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")

        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.open_files = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_files.setIcon(icon)
        self.open_files.setObjectName("open_files")

        self.born_mid_codes = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/siyuanshi.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.born_mid_codes.setIcon(icon1)
        self.born_mid_codes.setObjectName("born_mid_codes")

        self.born_mid_codes_better = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/youhua.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.born_mid_codes_better.setIcon(icon2)
        self.born_mid_codes_better.setObjectName("born_mid_codes_better")

        self.born8086 = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/huibian.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.born8086.setIcon(icon3)
        self.born8086.setObjectName("born8086")

        self.quit_action = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("images/quit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.quit_action.setIcon(icon4)
        self.quit_action.setObjectName("quit_action")

        self.toolBar.addAction(self.open_files)
        self.toolBar.addAction(self.born_mid_codes)
        self.toolBar.addAction(self.born_mid_codes_better)
        self.toolBar.addAction(self.born8086)
        self.toolBar.addAction(self.quit_action)


        hbox = QHBoxLayout()
        hbox.addWidget(self.textEdit)
        hbox.addWidget(self.textBrowser)
        widget_for_layout = QWidget()
        widget_for_layout.setLayout(hbox)
        MainWindow.setCentralWidget(widget_for_layout)



        self.retranslateUi(MainWindow)
        self.quit_action.triggered['bool'].connect(MainWindow.close)
        self.open_files.triggered['bool'].connect(self.open_file)
        self.born_mid_codes_better.triggered['bool'].connect(self.get_mid_code_better)
        self.born_mid_codes.triggered['bool'].connect(self.get_mid_code)
        self.born8086.triggered['bool'].connect(self.born8086_run)

        save_action = QAction(self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered['bool'].connect(self.save_file)
        self.textEdit.addAction(save_action)
        # self.toolBar.addAction(save_action)


        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle(_translate("MainWindow", "Compiler"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))

        self.open_files.setText(_translate("MainWindow", "打开文件"))
        self.open_files.setToolTip(_translate("MainWindow", "打开文件"))
        self.open_files.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.born_mid_codes.setText(_translate("MainWindow", "生成四元式"))
        self.born_mid_codes.setToolTip(_translate("MainWindow", "生成四元式"))
        self.born_mid_codes.setShortcut(_translate("MainWindow", "F3"))
        self.born_mid_codes_better.setText(_translate("MainWindow", "优化四元式生成"))
        self.born_mid_codes_better.setToolTip(_translate("MainWindow", "生成优化四元式"))
        self.born_mid_codes_better.setShortcut(_translate("MainWindow", "F4"))
        self.born8086.setText(_translate("MainWindow", "汇编生成"))
        self.born8086.setToolTip(_translate("MainWindow", "生成汇编代码"))
        self.born8086.setShortcut(_translate("MainWindow", "F5"))

        self.quit_action.setText(_translate("MainWindow", "退出"))
        self.quit_action.setToolTip(_translate("MainWindow", "退出程序"))
        self.quit_action.setShortcut(_translate("MainWindow", "Ctrl+Q"))

    def open_file(self):
        self.openfile_name, file_type = QFileDialog.getOpenFileName(self, '选择文件', '', 'C (*.c , *.cpp)')

        with open(self.openfile_name,"r") as f:
            code = f.read()

        self.textEdit.setText(code)
        self.textBrowser.setText("")

    def save_file(self):
        if self.openfile_name != "":
            code = self.textEdit.text()
            with open(self.openfile_name, "w") as f:
                f.write(code)

    def get_mid_code_better(self):
        try:
            code = self.textEdit.text()
            with open("v.cpp", "w") as f:
                f.write(code)
            mid_codes = self.LRAnalysier.analyse(code)
            o = Optimizer()
            o.load_mid_codes(mid_codes)
            o.run()
            mid_codes = o.get_result()
            res = str()
            for m in mid_codes:
                if str(m) == "":
                    continue
                res += str(m)
                res += "\n"
            self.textBrowser.setText(res)
        except Exception as e:
            self.textBrowser.setText("")
            reply = QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def get_mid_code(self):
        try:
            code = self.textEdit.text()
            with open("v.cpp", "w") as f:
                f.write(code)
            mid_codes = self.LRAnalysier.analyse(code)
            res = str()
            for m in mid_codes:
                if str(m) == "":
                    continue
                res += str(m)
                res += "\n"
            self.textBrowser.setText(res)
        except Exception as e:
            self.textBrowser.setText("")
            reply = QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)



    def born8086_run(self):
        # TODO 输出8086代码
        try:
            code = self.textEdit.text()
            with open("v.cpp", "w") as f:
                f.write(code)
            if code == "":
                return
            else:
                mid_codes = self.LRAnalysier.analyse(code)
                o = Optimizer()
                o.load_mid_codes(mid_codes)
                o.run()
                mid_codes = o.get_result()
                t = Target_fun()
                t.load_mid_codes(mid_codes)
                t.run()
                res = str()
                for l in t.out_put_block:
                    res += l
                    res += "\n"
                self.textBrowser.setText(res)
                with open("/home/bing/Masm/V.ASM", "w") as f:
                    for l in t.out_put_block:
                        f.write(l)
                        f.write("\n")
                t = threading.Thread(target=self.dos, args=("dosbox",))
                t.start()
        except Exception as e:
            self.textBrowser.setText("")
            reply = QMessageBox.warning(self, "Error", str(e), QMessageBox.Ok)

    def dos(self, line):
        os.system(line)




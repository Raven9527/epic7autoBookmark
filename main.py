# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt6 UI code generator 6.1.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

from unittest import case
from PyQt6 import QtCore, QtGui, QtWidgets
from PIL import ImageGrab, Image
from functools import partial

import cv2
import pyautogui
import pytesseract
import pygetwindow
import json

file = open('config.json', 'r', encoding='utf-8')
config = json.load(file)
tesseract_path = config['tesseract_path'] 
bluestack_name = config['bluestack_name']

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
pytesseract.pytesseract.tesseract_cmd =  tesseract_path

class worker(QtCore.QThread):
    startMode = 0
    expectNum = 0

    isStart = QtCore.pyqtSignal()
    isProgress = QtCore.pyqtSignal(str)
    isFinish = QtCore.pyqtSignal()
    isError = QtCore.pyqtSignal()
    
    emitLog = QtCore.pyqtSignal(str)
    emitMoney = QtCore.pyqtSignal(str)
    emitStone = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def setVariable(self, startMode: int, expectNum: int):
        self.startMode = startMode
        self.expectNum = expectNum

    def run(self):
        self.isStart.emit()

        print("startMode: ", self.startMode)
        print("expectedNum: ", self.expectNum)

        try:
            self.emitLog.emit("===== 初始化 =====")

            QtCore.QThread.sleep(1)

            self.emitLog.emit("取得模擬器位置...")

            QtCore.QThread.sleep(1)

            bluestack_window = pygetwindow.getWindowsWithTitle(bluestack_name)[0]
            if not bluestack_window:
                self.emitLog.emit("錯誤: 取得失敗")
                raise ValueError("Window location not found")

            self.emitLog.emit("取得成功")

            QtCore.QThread.sleep(1)

            self.emitLog.emit("調整模擬器大小...")

            bluestack_window.size = (1245, 733)

            QtCore.QThread.sleep(1)

            self.emitLog.emit("調整成功")

            QtCore.QThread.sleep(1)

            self.emitLog.emit("定位圖像辨識位置...")

            QtCore.QThread.sleep(1)

            stoneImgLocation = pyautogui.locateOnScreen('./img/stone.png', confidence=0.95)
            if not stoneImgLocation:
                self.emitLog.emit("錯誤: 定位失敗")
                raise ValueError("Stone location not found")

            self.emitLog.emit("定位成功")

            QtCore.QThread.sleep(1)

            self.emitLog.emit("取得錢錢和天空石...")

            moneyImg = pyautogui.screenshot(region=(stoneImgLocation.left-240, stoneImgLocation.top, stoneImgLocation.width+240, stoneImgLocation.height+5))
            res = pytesseract.image_to_string(moneyImg, lang='eng', \
                    config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789').rstrip()

            #self.emitLog.emit(f"錢錢: {res}")
            self.emitMoney.emit(res)
            moneyNum = int(res)

            stoneImg = pyautogui.screenshot(region=(stoneImgLocation.left, stoneImgLocation.top, stoneImgLocation.width+100, stoneImgLocation.height+5))
            res = pytesseract.image_to_string(stoneImg, lang='eng', \
                    config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789').rstrip()

            #self.emitLog.emit(f"天空石: {res}")
            self.emitStone.emit(res)
            stoneNum = int(res)
            
            QtCore.QThread.sleep(1)
            
            self.emitLog.emit("取得成功")

            QtCore.QThread.sleep(1)

            # check input
            if moneyNum < 280000:
                self.emitLog.emit("錯誤: 金幣不足28萬")
                raise ValueError("out of money")

            if stoneNum < 3:
                self.emitLog.emit("錯誤: 天空石不足以刷新商店")
                raise ValueError("out of stone")
            
            if self.startMode == 3 and self.expectNum > stoneNum:
                self.emitLog.emit("錯誤: 天空石使用數量大於持有數量")
                raise ValueError("stone input error")

            self.emitLog.emit("初始化完成")

            QtCore.QThread.sleep(1)

            self.emitLog.emit("===== 刷商店 =====")

            QtCore.QThread.sleep(1)

            refreshTime = 0
            covenantFoundTime = 0
            mysticFoundTime = 0

            # mode 1 & mode 2
            if self.startMode != 3:
                needRefresh = False
                while self.expectNum > 0 and moneyNum > 280000 and stoneNum >= 3:
                    covenantLocation = pyautogui.locateOnScreen('./img/covenantLocation.png', confidence=0.95)
                    if covenantLocation:
                        print("find covenant!")
                        self.emitLog.emit("找到聖約書籤")
                        pyautogui.click(pyautogui.center((covenantLocation.left+500, covenantLocation.top, 160, covenantLocation.height)))

                        QtCore.QThread.sleep(1)

                        while True:
                            buyButton = pyautogui.locateOnScreen('./img/buyButton.png', confidence=0.95)
                            if buyButton:
                                pyautogui.click(pyautogui.center(buyButton))

                                if self.startMode == 1:
                                    self.expectNum -= 1
                                    self.emitLog.emit(f"剩餘次數: {self.expectNum}次")
                                
                                moneyNum = moneyNum - 184000
                                covenantFoundTime += 1
                                self.emitMoney.emit(str(moneyNum))

                                break
                            QtCore.QThread.sleep(1)

                        QtCore.QThread.sleep(1)
                    else:
                        print("not find covenant!")

                    QtCore.QThread.sleep(1)

                    mysticLocation = pyautogui.locateOnScreen('./img/mysticLocation.png', confidence=0.95)
                    if mysticLocation:
                        print("find mystic!")
                        self.emitLog.emit("找到神秘書籤")
                        pyautogui.click(pyautogui.center((mysticLocation.left+500, mysticLocation.top, 160, mysticLocation.height)))
                        
                        QtCore.QThread.sleep(1)

                        while True:
                            buyButton = pyautogui.locateOnScreen('./img/buyButton.png', confidence=0.95)
                            if buyButton:
                                pyautogui.click(pyautogui.center(buyButton))

                                if self.startMode == 2:
                                    self.expectNum -= 1
                                    self.emitLog.emit(f"剩餘次數: {self.expectNum}次")

                                moneyNum = moneyNum - 280000
                                mysticFoundTime += 1
                                self.emitMoney.emit(str(moneyNum))

                                break
                            QtCore.QThread.sleep(1)

                        QtCore.QThread.sleep(1)

                    else:
                        print("not find mystic!")

                    QtCore.QThread.sleep(1)

                    if needRefresh:
                        refreshButton = pyautogui.locateOnScreen('./img/refreshButton.png', confidence=0.95)
                        if refreshButton:
                            pyautogui.click(pyautogui.center(refreshButton))

                            QtCore.QThread.sleep(1)

                            refreshYesButton = pyautogui.locateOnScreen('./img/refreshYesButton.png', confidence=0.95)
                            if refreshYesButton:
                                pyautogui.click(pyautogui.center(refreshYesButton))

                                stoneNum = stoneNum - 3
                                self.emitStone.emit(str(stoneNum))
                                
                                refreshTime += 1

                                needRefresh = False

                                QtCore.QThread.sleep(3)

                    else:
                        # drag down
                        pyautogui.moveTo(stoneImgLocation.left, stoneImgLocation.top+500)
                        pyautogui.drag(0, -300, 0.4, button='left')

                        needRefresh = True

                        QtCore.QThread.sleep(1)

            # mode 3
            else:
                needRefresh = False
                while self.expectNum >= 3 and moneyNum > 280000 and stoneNum >= 3:
                    covenantLocation = pyautogui.locateOnScreen('./img/covenantLocation.png', confidence=0.95)
                    if covenantLocation:
                        print("find covenant!")
                        self.emitLog.emit("找到聖約書籤")
                        pyautogui.click(pyautogui.center((covenantLocation.left+500, covenantLocation.top, 160, covenantLocation.height)))

                        QtCore.QThread.sleep(1)

                        while True:
                            buyButton = pyautogui.locateOnScreen('./img/buyButton.png', confidence=0.95)
                            if buyButton:
                                pyautogui.click(pyautogui.center(buyButton))
                                
                                moneyNum = moneyNum - 184000
                                covenantFoundTime += 1
                                self.emitMoney.emit(str(moneyNum))

                                break
                            QtCore.QThread.sleep(1)

                        QtCore.QThread.sleep(1)
                    else:
                        print("not find covenant!")

                    QtCore.QThread.sleep(1)

                    mysticLocation = pyautogui.locateOnScreen('./img/mysticLocation.png', confidence=0.95)
                    if mysticLocation:
                        print("find mystic!")
                        self.emitLog.emit("找到神秘書籤")
                        pyautogui.click(pyautogui.center((mysticLocation.left+500, mysticLocation.top, 160, mysticLocation.height)))
                        
                        QtCore.QThread.sleep(1)

                        while True:
                            buyButton = pyautogui.locateOnScreen('./img/buyButton.png', confidence=0.95)
                            if buyButton:
                                pyautogui.click(pyautogui.center(buyButton))

                                moneyNum = moneyNum - 280000
                                mysticFoundTime += 1
                                self.emitMoney.emit(str(moneyNum))

                                break
                            QtCore.QThread.sleep(1)

                        QtCore.QThread.sleep(1)

                    else:
                        print("not find mystic!")

                    QtCore.QThread.sleep(1)

                    if needRefresh:
                        refreshButton = pyautogui.locateOnScreen('./img/refreshButton.png', confidence=0.95)
                        if refreshButton:
                            pyautogui.click(pyautogui.center(refreshButton))

                            QtCore.QThread.sleep(1)

                            refreshYesButton = pyautogui.locateOnScreen('./img/refreshYesButton.png', confidence=0.95)
                            if refreshYesButton:
                                pyautogui.click(pyautogui.center(refreshYesButton))

                                stoneNum = stoneNum - 3
                                self.emitStone.emit(str(stoneNum))
                                
                                refreshTime += 1

                                self.expectNum -= 3
                                self.emitLog.emit(f"剩餘次數: {int(self.expectNum/3)}次")

                                needRefresh = False

                                QtCore.QThread.sleep(3)

                    else:
                        # drag down
                        pyautogui.moveTo(stoneImgLocation.left, stoneImgLocation.top+500)
                        pyautogui.drag(0, -300, 0.4, button='left')

                        needRefresh = True

                        QtCore.QThread.sleep(1)

            # finished report
            self.emitLog.emit("===== 結算 =====")
            self.emitLog.emit("共花費:")
            self.emitLog.emit(f"天空石: {refreshTime*3}個")
            self.emitLog.emit(f"金幣: {covenantFoundTime*184000+mysticFoundTime*280000}元")
            self.emitLog.emit("獲得書籤:")
            self.emitLog.emit(f"聖約: {covenantFoundTime}次")
            self.emitLog.emit(f"神秘: {mysticFoundTime}次")

            self.isFinish.emit()

        except Exception as e:
            print(e)
            # self.emitLog.emit(str(e))
            self.isError.emit()

class Ui_Main(object):
    start = False

    def setupUi(self, Main):
        Main.setObjectName("Main")
        Main.resize(310, 460)
        Main.setMinimumSize(QtCore.QSize(310, 460))
        Main.setMaximumSize(QtCore.QSize(310, 460))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        Main.setFont(font)
        self.tabWidget = QtWidgets.QTabWidget(Main)
        self.tabWidget.setGeometry(QtCore.QRect(5, 5, 300, 450))
        self.tabWidget.setMinimumSize(QtCore.QSize(300, 450))
        self.tabWidget.setMaximumSize(QtCore.QSize(300, 450))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.tabWidget.setFont(font)
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setObjectName("tabWidget")
        self.functionTab = QtWidgets.QWidget()
        self.functionTab.setMinimumSize(QtCore.QSize(300, 450))
        self.functionTab.setMaximumSize(QtCore.QSize(300, 450))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.functionTab.setFont(font)
        self.functionTab.setObjectName("functionTab")
        self.covenantInput = QtWidgets.QLineEdit(self.functionTab)
        self.covenantInput.setGeometry(QtCore.QRect(140, 90, 70, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.covenantInput.setFont(font)
        self.covenantInput.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.covenantInput.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.covenantInput.setObjectName("covenantInput")
        self.mysticInput = QtWidgets.QLineEdit(self.functionTab)
        self.mysticInput.setGeometry(QtCore.QRect(140, 130, 70, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.mysticInput.setFont(font)
        self.mysticInput.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.mysticInput.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.mysticInput.setObjectName("mysticInput")
        self.moneyTextShowLabel = QtWidgets.QLabel(self.functionTab)
        self.moneyTextShowLabel.setGeometry(QtCore.QRect(40, 10, 60, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.moneyTextShowLabel.setFont(font)
        self.moneyTextShowLabel.setObjectName("moneyTextShowLabel")
        self.moneyTotalShowLabel = QtWidgets.QLabel(self.functionTab)
        self.moneyTotalShowLabel.setGeometry(QtCore.QRect(140, 10, 90, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.moneyTotalShowLabel.setFont(font)
        self.moneyTotalShowLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.moneyTotalShowLabel.setObjectName("moneyTotalShowLabel")
        self.divider = QtWidgets.QFrame(self.functionTab)
        self.divider.setGeometry(QtCore.QRect(10, 60, 271, 20))
        self.divider.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.divider.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.divider.setObjectName("divider")
        self.stoneTextShowLabel = QtWidgets.QLabel(self.functionTab)
        self.stoneTextShowLabel.setGeometry(QtCore.QRect(40, 40, 60, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.stoneTextShowLabel.setFont(font)
        self.stoneTextShowLabel.setObjectName("stoneTextShowLabel")
        self.stoneTotalShowLabel = QtWidgets.QLabel(self.functionTab)
        self.stoneTotalShowLabel.setGeometry(QtCore.QRect(140, 40, 90, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.stoneTotalShowLabel.setFont(font)
        self.stoneTotalShowLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.stoneTotalShowLabel.setObjectName("stoneTotalShowLabel")
        self.startButton = QtWidgets.QPushButton(self.functionTab)
        self.startButton.setGeometry(QtCore.QRect(140, 360, 100, 40))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.startButton.setFont(font)
        self.startButton.setStyleSheet("")
        self.startButton.setDefault(False)
        self.startButton.setFlat(False)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(self.startPressEvent)
        self.covenantTimeLabel = QtWidgets.QLabel(self.functionTab)
        self.covenantTimeLabel.setGeometry(QtCore.QRect(220, 90, 20, 20))
        self.covenantTimeLabel.setObjectName("covenantTimeLabel")
        self.mysticTimeLabel = QtWidgets.QLabel(self.functionTab)
        self.mysticTimeLabel.setGeometry(QtCore.QRect(220, 130, 20, 20))
        self.mysticTimeLabel.setObjectName("mysticTimeLabel")
        self.logTextBrowser = QtWidgets.QTextBrowser(self.functionTab)
        self.logTextBrowser.setGeometry(QtCore.QRect(40, 210, 200, 131))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.logTextBrowser.setFont(font)
        self.logTextBrowser.setObjectName("logTextBrowser")
        self.stoneTimeLabel = QtWidgets.QLabel(self.functionTab)
        self.stoneTimeLabel.setGeometry(QtCore.QRect(220, 170, 20, 20))
        self.stoneTimeLabel.setObjectName("stoneTimeLabel")
        self.stoneInput = QtWidgets.QLineEdit(self.functionTab)
        self.stoneInput.setGeometry(QtCore.QRect(140, 170, 70, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.stoneInput.setFont(font)
        self.stoneInput.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.stoneInput.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTrailing|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.stoneInput.setObjectName("stoneInput")
        self.covenantRadioButton = QtWidgets.QRadioButton(self.functionTab)
        self.covenantRadioButton.setGeometry(QtCore.QRect(40, 90, 91, 21))
        self.covenantRadioButton.setChecked(True)
        self.covenantRadioButton.setObjectName("covenantRadioButton")
        self.mysticRadioButton = QtWidgets.QRadioButton(self.functionTab)
        self.mysticRadioButton.setGeometry(QtCore.QRect(40, 130, 91, 21))
        self.mysticRadioButton.setObjectName("mysticRadioButton")
        self.stoneRadioButton = QtWidgets.QRadioButton(self.functionTab)
        self.stoneRadioButton.setGeometry(QtCore.QRect(40, 170, 91, 21))
        self.stoneRadioButton.setObjectName("stoneRadioButton")
        self.tabWidget.addTab(self.functionTab, "")
        self.introductionTab = QtWidgets.QWidget()
        self.introductionTab.setMinimumSize(QtCore.QSize(300, 450))
        self.introductionTab.setMaximumSize(QtCore.QSize(300, 450))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.introductionTab.setFont(font)
        self.introductionTab.setObjectName("introductionTab")
        self.textBrowser = QtWidgets.QTextBrowser(self.introductionTab)
        self.textBrowser.setGeometry(QtCore.QRect(20, 200, 256, 192))
        self.textBrowser.setObjectName("textBrowser")
        self.githubText = QtWidgets.QLabel(self.introductionTab)
        self.githubText.setGeometry(QtCore.QRect(20, 20, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.githubText.setFont(font)
        self.githubText.setObjectName("githubText")
        self.githubTextUrl = QtWidgets.QLabel(self.introductionTab)
        self.githubTextUrl.setGeometry(QtCore.QRect(20, 40, 251, 41))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(11)
        self.githubTextUrl.setFont(font)
        self.githubTextUrl.setScaledContents(False)
        self.githubTextUrl.setWordWrap(True)
        self.githubTextUrl.setOpenExternalLinks(True)
        self.githubTextUrl.setObjectName("githubTextUrl")
        self.tabWidget.addTab(self.introductionTab, "")

        self.worker = worker()
        self.worker.isStart.connect(self.startWorker)
        self.worker.isFinish.connect(self.stopWorker)
        self.worker.isError.connect(self.errorWorker)

        self.worker.emitLog.connect(lambda text: self.logTextBrowser.append(text))
        self.worker.emitMoney.connect(lambda text: self.moneyTotalShowLabel.setText(text))
        self.worker.emitStone.connect(lambda text: self.stoneTotalShowLabel.setText(text))

        self.retranslateUi(Main)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Main)

    def retranslateUi(self, Main):
        _translate = QtCore.QCoreApplication.translate
        Main.setWindowTitle(_translate("Main", "第七史詩刷商店小工具"))
        self.covenantInput.setText(_translate("Main", "0"))
        self.mysticInput.setText(_translate("Main", "0"))
        self.moneyTextShowLabel.setText(_translate("Main", "金幣"))
        self.moneyTotalShowLabel.setText(_translate("Main", "0"))
        self.stoneTextShowLabel.setText(_translate("Main", "天空石"))
        self.stoneTotalShowLabel.setText(_translate("Main", "0"))
        self.startButton.setText(_translate("Main", "開始"))
        self.covenantTimeLabel.setText(_translate("Main", "次"))
        self.mysticTimeLabel.setText(_translate("Main", "次"))
        self.logTextBrowser.setHtml(_translate("Main", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'微軟正黑體\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">毫無反應, 就是個小工具</p></body></html>"))
        self.stoneTimeLabel.setText(_translate("Main", "個"))
        self.stoneInput.setText(_translate("Main", "0"))
        self.covenantRadioButton.setText(_translate("Main", "聖約書籤"))
        self.mysticRadioButton.setText(_translate("Main", "神秘書籤"))
        self.stoneRadioButton.setText(_translate("Main", "天空石"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.functionTab), _translate("Main", "功能"))
        self.textBrowser.setHtml(_translate("Main", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'微軟正黑體\'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">啟動條件:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">金幣至少280000元</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">天空石至少3個</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">填的數字為停止的條件，</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">刷到的神秘與聖約都會買，</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">目前沒有只買某種的功能，</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">未來也不會做。</p></body></html>"))
        self.githubText.setText(_translate("Main", "GitHub:"))
        self.githubTextUrl.setText(_translate("Main", "<a href=\"https://www.github.com/steven010116/epic7autoBookmark\">https://www.github.com/steven010116/epic7autoBookmark</a>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.introductionTab), _translate("Main", "簡介"))


    def startPressEvent(self):
        self.start = not self.start
        
        if(self.start):
            startMode = 0
            expectNum = 0
            if self.covenantRadioButton.isChecked():
                startMode = 1
                covenant = self.covenantInput.text()
                expectNum = int(covenant) if covenant.isdigit() else 0
                self.covenantInput.setText(str(expectNum))

            elif self.mysticRadioButton.isChecked():
                startMode = 2
                mystic = self.mysticInput.text()
                expectNum = int(mystic) if mystic.isdigit() else 0
                self.mysticInput.setText(str(expectNum))

            elif self.stoneRadioButton.isChecked():
                startMode = 3
                stone = self.stoneInput.text()
                expectNum = int(stone) if stone.isdigit() else 0
                self.stoneInput.setText(str(expectNum))

            else:
                self.logTextBrowser.append("沒有選取的radioButton,")
                self.logTextBrowser.append("明明就預設會選一個,")
                self.logTextBrowser.append("你是怎麼取消掉的? 能不能教我?")
                self.logTextBrowser.append("===== 停止 =====")
                self.startProperty(False)
                return

            self.worker.setVariable(startMode, expectNum)
            self.worker.start()
        else:
            self.worker.terminate()
            self.logTextBrowser.append("===== 停止 =====")
            self.startProperty(False)

    def startProperty(self, isDisabled: bool):
        if(isDisabled):
            self.startButton.setText("停止")
        else:
            self.startButton.setText("開始")

        self.covenantRadioButton.setDisabled(isDisabled)
        self.mysticRadioButton.setDisabled(isDisabled)
        self.stoneRadioButton.setDisabled(isDisabled)
        self.covenantInput.setDisabled(isDisabled)
        self.mysticInput.setDisabled(isDisabled)
        self.stoneInput.setDisabled(isDisabled)

    def startWorker(self):
        self.logTextBrowser.setText("")
        self.moneyTotalShowLabel.setText("0")
        self.stoneTotalShowLabel.setText("0")
        self.startProperty(True)

    def errorWorker(self):
        self.start = False
        self.startProperty(False)

    def stopWorker(self):
        self.start = False
        self.startProperty(False)
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('main.ico'))

    Main = QtWidgets.QWidget()
    ui = Ui_Main()
    ui.setupUi(Main)
    Main.show()
    sys.exit(app.exec())
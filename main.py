# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt6 UI code generator 6.1.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt6 import QtCore, QtGui, QtWidgets

from adbutils import adb, AdbDevice
from numpy import asarray
import aircv
import json
import random

file = open("config.json", "r", encoding="utf-8")
config = json.load(file)
adb_addr = config["adb_addr"]
e7_language = config["e7_language"]


def pointOffset(point):
    x = int(random.uniform(point.x - 2, point.x + 2))
    y = int(random.uniform(point.y - 2, point.y + 2))
    return (x, y)


def doubleClick(device: AdbDevice, x: int, y: int):
    device.click(x, y)
    device.click(x, y)


class worker(QtCore.QThread):
    startMode = 0
    expectNum = 0
    moneyNum = 0
    stoneNum = 0

    isStart = QtCore.pyqtSignal()
    isProgress = QtCore.pyqtSignal(str)
    isFinish = QtCore.pyqtSignal()
    isError = QtCore.pyqtSignal()

    emitLog = QtCore.pyqtSignal(str)
    emitMoney = QtCore.pyqtSignal(str)
    emitStone = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def setVariable(self, startMode: int, expectNum: int, moneyNum: int, stoneNum: int, autoRestartDispatch: bool):
        self.startMode = startMode
        self.expectNum = expectNum
        self.moneyNum = moneyNum
        self.stoneNum = stoneNum
        self.autoRestartDispatch = autoRestartDispatch

    def processDispatchMissionComplete(self, device, restartDispatchButton):
        if not self.autoRestartDispatch:
            return
        
        screenshot = asarray(device.screenshot())
        condifence = 0.75
        restartDispatchButtonLocation = aircv.find_template(screenshot, restartDispatchButton, condifence)
        
        if restartDispatchButtonLocation:
            print("dispatch mission completed!")
            self.emitLog.emit("重新進行派遣任務")
            
            while True:
                restartDispatchFoundResult: tuple = restartDispatchButtonLocation["result"]
                doubleClick(
                    device,
                    restartDispatchFoundResult[0],
                    restartDispatchFoundResult[1],
                )
                
                QtCore.QThread.sleep(1)

                doubleClick(
                    device,
                    restartDispatchFoundResult[0],
                    restartDispatchFoundResult[1],
                )
                
                QtCore.QThread.sleep(1)

                after_restartDispatch_screenshot = asarray(device.screenshot())
                restartDispatchButtonLocationAfter = aircv.find_template(
                    after_restartDispatch_screenshot, restartDispatchButton, condifence
                )
                
                if not restartDispatchButtonLocationAfter:
                    break
                
            QtCore.QThread.sleep(1)

    def run(self):
        self.isStart.emit()

        print("startMode: ", self.startMode)
        print("expectedNum: ", self.expectNum)

        try:
            self.emitLog.emit("===== 初始化 =====")

            QtCore.QThread.sleep(1)

            # check input
            if self.moneyNum < 280000:
                self.emitLog.emit("錯誤: 金幣不足28萬")
                raise ValueError("out of money")

            if self.stoneNum < 3:
                self.emitLog.emit("錯誤: 天空石不足以刷新商店")
                raise ValueError("out of stone")

            if self.startMode == 3 and self.expectNum > self.stoneNum:
                self.emitLog.emit("錯誤: 天空石使用數量大於持有數量")
                raise ValueError("stone input error")

            self.emitLog.emit("正在嘗試連接模擬器......")

            QtCore.QThread.sleep(1)

            adb.connect(adb_addr, timeout=10)

            device = adb.device(serial=adb_addr)

            self.emitLog.emit("adb連接成功")

            QtCore.QThread.sleep(1)

            self.emitLog.emit("初始化完成")

            QtCore.QThread.sleep(1)

            self.emitLog.emit("===== 刷商店 =====")

            QtCore.QThread.sleep(1)

            refreshTime = 0
            covenantFoundTime = 0
            mysticFoundTime = 0

            covenant = aircv.imread("./img/covenantLocation.png")
            mystic = aircv.imread("./img/mysticLocation.png")
            buyButton = aircv.imread(f"./img/buyButton-{e7_language}.png")
            refreshButton = aircv.imread(f"./img/refreshButton-{e7_language}.png")
            refreshYesButton = aircv.imread(f"./img/refreshYesButton-{e7_language}.png")
            restartDispatchButton = aircv.imread(f"./img/restartDispatchButton-{e7_language}.png")
            
            needRefresh = False
            covenantFound = False
            mysticFound = False

            if self.startMode == 3:
                self.expectNum = self.expectNum // 3
            
            while self.expectNum >= 0 and self.moneyNum > 280000 and self.stoneNum >= 3:                
                
                screenshot = asarray(device.screenshot())

                covenantLocation = aircv.find_template(screenshot, covenant, 0.9)
                if covenantLocation and (not covenantFound):
                    covenantFound = True

                    print("find covenant!")
                    self.emitLog.emit("找到聖約書籤")

                    while True:
                        covenantFoundResult: tuple = covenantLocation["result"]
                        doubleClick(
                            device,
                            covenantFoundResult[0] + 800,
                            covenantFoundResult[1] + 40,
                        )

                        QtCore.QThread.sleep(1)
                        
                        self.processDispatchMissionComplete(device, restartDispatchButton)

                        buy_screenshot = asarray(device.screenshot())
                        buyButtonLocation = aircv.find_template(
                            buy_screenshot, buyButton, 0.9
                        )

                        if buyButtonLocation:
                            buyButtonFoundResult: tuple = buyButtonLocation["result"]

                            while True:
                                doubleClick(
                                    device,
                                    buyButtonFoundResult[0],
                                    buyButtonFoundResult[1],
                                )

                                QtCore.QThread.sleep(1)
                                
                                self.processDispatchMissionComplete(device, restartDispatchButton)

                                after_buy_screenshot = asarray(device.screenshot())
                                buyButtonLocationAfter = aircv.find_template(
                                    after_buy_screenshot, buyButton, 0.9, True
                                )

                                if not buyButtonLocationAfter:
                                    break

                                QtCore.QThread.sleep(1)

                            if self.startMode == 1:
                                self.expectNum -= 1
                                self.emitLog.emit(f"剩餘次數: {self.expectNum}次")

                            self.moneyNum = self.moneyNum - 184000
                            covenantFoundTime += 1
                            self.emitMoney.emit(str(self.moneyNum))

                            break

                        QtCore.QThread.sleep(1)

                else:
                    print("not find covenant!")

                mysticLocation = aircv.find_template(screenshot, mystic, 0.9)
                if mysticLocation and (not mysticFound):
                    mysticFound = True

                    print("find mystic!")
                    self.emitLog.emit("找到神秘書籤")

                    while True:
                        mysticFoundResult: tuple = mysticLocation["result"]
                        doubleClick(
                            device,
                            mysticFoundResult[0] + 800,
                            mysticFoundResult[1] + 40,
                        )

                        QtCore.QThread.sleep(1)
                        
                        self.processDispatchMissionComplete(device, restartDispatchButton)

                        buy_screenshot = asarray(device.screenshot())
                        buyButtonLocation = aircv.find_template(
                            buy_screenshot, buyButton, 0.9
                        )

                        if buyButtonLocation:
                            buyButtonFoundResult: tuple = buyButtonLocation["result"]

                            while True:
                                doubleClick(
                                    device,
                                    buyButtonFoundResult[0],
                                    buyButtonFoundResult[1],
                                )

                                QtCore.QThread.sleep(1)
                                
                                self.processDispatchMissionComplete(device, restartDispatchButton)

                                after_buy_screenshot = asarray(device.screenshot())
                                buyButtonLocationAfter = aircv.find_template(
                                    after_buy_screenshot, buyButton, 0.9, True
                                )

                                if not buyButtonLocationAfter:
                                    break

                                QtCore.QThread.sleep(1)

                            if self.startMode == 2:
                                self.expectNum -= 1
                                self.emitLog.emit(f"剩餘次數: {self.expectNum}次")

                            self.moneyNum = self.moneyNum - 280000
                            mysticFoundTime += 1
                            self.emitMoney.emit(str(self.moneyNum))

                            break

                        QtCore.QThread.sleep(1)

                else:
                    print("not find mystic!")
                    
                if needRefresh:
                    if self.expectNum <= 0:
                        break
                    
                    refreshButtonLocation = aircv.find_template(
                        screenshot, refreshButton, 0.9
                    )
                    while True:
                        refreshButtonFoundResult: tuple = refreshButtonLocation[
                            "result"
                        ]
                        doubleClick(
                            device,
                            refreshButtonFoundResult[0],
                            refreshButtonFoundResult[1],
                        )
                        QtCore.QThread.sleep(1)

                        self.processDispatchMissionComplete(device, restartDispatchButton)

                        confirm_screenshot = asarray(device.screenshot())
                        refreshYesButtonLocation = aircv.find_template(
                            confirm_screenshot, refreshYesButton, 0.9
                        )

                        if refreshYesButtonLocation:
                            refreshYesButtonFoundResult: tuple = (
                                refreshYesButtonLocation["result"]
                            )

                            while True:
                                doubleClick(
                                    device,
                                    refreshYesButtonFoundResult[0],
                                    refreshYesButtonFoundResult[1],
                                )

                                QtCore.QThread.sleep(1)

                                self.processDispatchMissionComplete(device, restartDispatchButton)

                                after_click_yes_screenshot = asarray(
                                    device.screenshot()
                                )
                                refreshYesButtonLocation = aircv.find_template(
                                    after_click_yes_screenshot, refreshYesButton, 0.9
                                )

                                if not refreshYesButtonLocation:
                                    break

                                QtCore.QThread.sleep(1)

                            self.stoneNum = self.stoneNum - 3
                            self.emitStone.emit(str(self.stoneNum))

                            refreshTime += 1

                            if self.startMode == 3:
                                self.expectNum -= 1
                                self.emitLog.emit(f"剩餘次數: {int(self.expectNum)}次")

                            needRefresh = False
                            covenantFound = False
                            mysticFound = False

                            QtCore.QThread.sleep(1)

                            break

                        QtCore.QThread.sleep(1)

                else:
                    device.swipe(1400, 500, 1400, 200, 0.1)
                    needRefresh = True

                    QtCore.QThread.sleep(1)
                    self.processDispatchMissionComplete(device, restartDispatchButton)

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
        Main.setMinimumSize(QtCore.QSize(310, 500))
        Main.setMaximumSize(QtCore.QSize(310, 500))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        Main.setFont(font)
        self.tabWidget = QtWidgets.QTabWidget(Main)
        self.tabWidget.setGeometry(QtCore.QRect(5, 5, 300, 490))
        self.tabWidget.setMinimumSize(QtCore.QSize(300, 490))
        self.tabWidget.setMaximumSize(QtCore.QSize(300, 490))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.tabWidget.setFont(font)
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setObjectName("tabWidget")
        self.functionTab = QtWidgets.QWidget()
        self.functionTab.setMinimumSize(QtCore.QSize(300, 490))
        self.functionTab.setMaximumSize(QtCore.QSize(300, 490))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.functionTab.setFont(font)
        self.functionTab.setObjectName("functionTab")
        self.covenantInput = QtWidgets.QLineEdit(self.functionTab)
        self.covenantInput.setGeometry(QtCore.QRect(140, 130, 70, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.covenantInput.setFont(font)
        self.covenantInput.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.covenantInput.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.covenantInput.setObjectName("covenantInput")
        self.mysticInput = QtWidgets.QLineEdit(self.functionTab)
        self.mysticInput.setGeometry(QtCore.QRect(140, 170, 70, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.mysticInput.setFont(font)
        self.mysticInput.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.mysticInput.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.mysticInput.setObjectName("mysticInput")
        self.moneyTextShowLabel = QtWidgets.QLabel(self.functionTab)
        self.moneyTextShowLabel.setGeometry(QtCore.QRect(40, 10, 60, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.moneyTextShowLabel.setFont(font)
        self.moneyTextShowLabel.setObjectName("moneyTextShowLabel")
        self.moneyTotalShowEdit = QtWidgets.QLineEdit(self.functionTab)
        self.moneyTotalShowEdit.setGeometry(QtCore.QRect(120, 10, 111, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.moneyTotalShowEdit.setFont(font)
        self.moneyTotalShowEdit.setLayoutDirection(
            QtCore.Qt.LayoutDirection.RightToLeft
        )
        self.moneyTotalShowEdit.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.moneyTotalShowEdit.setObjectName("moneyTotalShowEdit")
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
        self.stoneTotalShowEdit = QtWidgets.QLineEdit(self.functionTab)
        self.stoneTotalShowEdit.setGeometry(QtCore.QRect(119, 40, 111, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.stoneTotalShowEdit.setFont(font)
        self.stoneTotalShowEdit.setLayoutDirection(
            QtCore.Qt.LayoutDirection.RightToLeft
        )
        self.stoneTotalShowEdit.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.stoneTotalShowEdit.setObjectName("stoneTotalShowEdit")
        self.startButton = QtWidgets.QPushButton(self.functionTab)
        self.startButton.setGeometry(QtCore.QRect(140, 400, 100, 40))
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
        self.covenantTimeLabel.setGeometry(QtCore.QRect(220, 130, 20, 20))
        self.covenantTimeLabel.setObjectName("covenantTimeLabel")
        self.mysticTimeLabel = QtWidgets.QLabel(self.functionTab)
        self.mysticTimeLabel.setGeometry(QtCore.QRect(220, 170, 20, 20))
        self.mysticTimeLabel.setObjectName("mysticTimeLabel")
        self.logTextBrowser = QtWidgets.QTextBrowser(self.functionTab)
        self.logTextBrowser.setGeometry(QtCore.QRect(40, 250, 200, 131))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.logTextBrowser.setFont(font)
        self.logTextBrowser.setObjectName("logTextBrowser")
        self.stoneTimeLabel = QtWidgets.QLabel(self.functionTab)
        self.stoneTimeLabel.setGeometry(QtCore.QRect(220, 210, 20, 20))
        self.stoneTimeLabel.setObjectName("stoneTimeLabel")
        self.stoneInput = QtWidgets.QLineEdit(self.functionTab)
        self.stoneInput.setGeometry(QtCore.QRect(140, 210, 70, 20))
        font = QtGui.QFont()
        font.setFamily("微軟正黑體")
        font.setPointSize(12)
        self.stoneInput.setFont(font)
        self.stoneInput.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.stoneInput.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.stoneInput.setObjectName("stoneInput")
        self.autoRestartDispatchCheckbox = QtWidgets.QCheckBox(self.functionTab)
        self.autoRestartDispatchCheckbox.setGeometry(QtCore.QRect(40, 90, 150, 21))
        self.autoRestartDispatchCheckbox.setObjectName("autoRestartDispatchCheckbox")
        self.autoRestartDispatchCheckbox.setChecked(False)
        self.covenantRadioButton = QtWidgets.QRadioButton(self.functionTab)
        self.covenantRadioButton.setGeometry(QtCore.QRect(40, 130, 91, 21))
        self.covenantRadioButton.setChecked(True)
        self.covenantRadioButton.setObjectName("covenantRadioButton")
        self.mysticRadioButton = QtWidgets.QRadioButton(self.functionTab)
        self.mysticRadioButton.setGeometry(QtCore.QRect(40, 170, 91, 21))
        self.mysticRadioButton.setObjectName("mysticRadioButton")
        self.stoneRadioButton = QtWidgets.QRadioButton(self.functionTab)
        self.stoneRadioButton.setGeometry(QtCore.QRect(40, 210, 91, 21))
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
        self.worker.emitMoney.connect(
            lambda text: self.moneyTotalShowEdit.setText(text)
        )
        self.worker.emitStone.connect(
            lambda text: self.stoneTotalShowEdit.setText(text)
        )

        self.retranslateUi(Main)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Main)

    def retranslateUi(self, Main):
        _translate = QtCore.QCoreApplication.translate
        Main.setWindowTitle(_translate("Main", "第七史詩刷商店小工具"))
        self.covenantInput.setText(_translate("Main", "0"))
        self.mysticInput.setText(_translate("Main", "0"))
        self.moneyTextShowLabel.setText(_translate("Main", "金幣"))
        self.moneyTotalShowEdit.setText(_translate("Main", "0"))
        self.stoneTextShowLabel.setText(_translate("Main", "天空石"))
        self.stoneTotalShowEdit.setText(_translate("Main", "0"))
        self.startButton.setText(_translate("Main", "開始"))
        self.covenantTimeLabel.setText(_translate("Main", "次"))
        self.mysticTimeLabel.setText(_translate("Main", "次"))
        self.logTextBrowser.setHtml(
            _translate(
                "Main",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'微軟正黑體'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">毫無反應, 就是個小工具</p></body></html>',
            )
        )
        self.stoneTimeLabel.setText(_translate("Main", "個"))
        self.stoneInput.setText(_translate("Main", "0"))
        self.autoRestartDispatchCheckbox.setText(_translate("Main", "自動重新派遣"))
        self.covenantRadioButton.setText(_translate("Main", "聖約書籤"))
        self.mysticRadioButton.setText(_translate("Main", "神秘書籤"))
        self.stoneRadioButton.setText(_translate("Main", "天空石"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.functionTab), _translate("Main", "功能")
        )
        self.textBrowser.setHtml(
            _translate(
                "Main",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'微軟正黑體'; font-size:12pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">啟動條件:</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">金幣至少280000元</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">天空石至少3個</p>\n'
                '<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">填的數字為停止的條件，</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">刷到的神秘與聖約都會買，</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">目前沒有只買某種的功能，</p>\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">未來也不會做。</p></body></html>',
            )
        )
        self.githubText.setText(_translate("Main", "GitHub:"))
        self.githubTextUrl.setText(
            _translate(
                "Main",
                '<a href="https://www.github.com/steven010116/epic7autoBookmark">https://www.github.com/steven010116/epic7autoBookmark</a>',
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.introductionTab), _translate("Main", "簡介")
        )

    def startPressEvent(self):
        self.start = not self.start

        if self.start:
            startMode = 0
            expectNum = 0
            moneyNum = (
                int(self.moneyTotalShowEdit.text())
                if self.moneyTotalShowEdit.text().isdigit()
                else 0
            )
            stoneNum = (
                int(self.stoneTotalShowEdit.text())
                if self.stoneTotalShowEdit.text().isdigit()
                else 0
            )
            autoRestartDispatch = self.autoRestartDispatchCheckbox.isChecked()

            if moneyNum == 0 or stoneNum == 0:
                self.logTextBrowser.setText("")
                self.logTextBrowser.append("石頭或金幣輸入錯誤")
                self.logTextBrowser.append("===== 停止 =====")
                self.start = not self.start
                self.startProperty(False)
                return

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
                self.start = not self.start
                self.startProperty(False)
                return

            self.worker.setVariable(startMode, expectNum, moneyNum, stoneNum, autoRestartDispatch)
            self.worker.start()
        else:
            self.worker.terminate()
            self.logTextBrowser.append("===== 停止 =====")
            self.startProperty(False)

    def startProperty(self, isDisabled: bool):
        if isDisabled:
            self.startButton.setText("停止")
        else:
            self.startButton.setText("開始")

        self.covenantRadioButton.setDisabled(isDisabled)
        self.mysticRadioButton.setDisabled(isDisabled)
        self.stoneRadioButton.setDisabled(isDisabled)
        self.moneyTotalShowEdit.setDisabled(isDisabled)
        self.stoneTotalShowEdit.setDisabled(isDisabled)
        self.covenantInput.setDisabled(isDisabled)
        self.mysticInput.setDisabled(isDisabled)
        self.stoneInput.setDisabled(isDisabled)
        self.autoRestartDispatchCheckbox.setDisabled(isDisabled)

    def startWorker(self):
        self.logTextBrowser.setText("")
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
    app.setWindowIcon(QtGui.QIcon("main.ico"))

    Main = QtWidgets.QWidget()
    ui = Ui_Main()
    ui.setupUi(Main)
    Main.show()
    sys.exit(app.exec())

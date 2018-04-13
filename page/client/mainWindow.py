from graduation.page.client import ui_mainWindow
from PyQt5 import QtWidgets,QtGui
from graduation.diagnosis import testclassify
from graduation.KNN import test
import dicom
# from tkinter import filedialog as tkFileDialog
from tensorflowCNN import preprocess
from PIL import Image, ImageTk
import numpy as np
from matplotlib import pyplot as plt
from graduation.threemethod import extract_train_test
import os

class firstWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = ui_mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.openButton.clicked.connect(self.openFile)
        self.ui.IncButton.clicked.connect(self.inception)
        self.ui.caButton.clicked.connect(self.getseed)
        self.ui.knnButton.clicked.connect(self.getKnn)
        self.ui.diaButton.clicked.connect(self.test)
        self.fileName = ""

    def inception(self):
        if (self.fileName != "") & ("jpg" not in self.fileName):
            fileNamelist = self.fileName.split("PT/PT_")
            self.fileNameShow = fileNamelist[0] + "merge/" + fileNamelist[1] + ".jpg"
            # print(self.fileNameShow)
            self.Flag = testclassify.testOne(self.fileNameShow)
            if self.Flag == True:
                self.ui.result.setText("正常")
                # print("正常")
            else:
                # print("异常")
                self.ui.result.setText("异常")
                # 打开文件
        elif "jpg"  in self.fileName:
            print(self.fileName)
            self.Flag = testclassify.testOne(self.fileName)
            if self.Flag == True:
                self.ui.result.setText("正常")
                # print("正常")
            else:
                # print("异常")
                self.ui.result.setText("异常")
        else:
            print("请选择文件")

    def test(self):
        flag = testclassify.testOne(r"C:/Users/FEITENG/Desktop/trainP/positive_005.jpg")
        print(flag)
    def getKnn(self):
        if (self.fileName != "") & ("jpg" not in self.fileName):
            fileNamelist = self.fileName.split("PT/PT_")
            self.fileNameShow = fileNamelist[0] + "merge/" + fileNamelist[1] + ".jpg"
            self.result = test.predict(self.fileNameShow)
            if self.result == True:
                self.ui.result.setText("正常")
                # print("正常")
            else:
                # print("异常")
                self.ui.result.setText("异常")
        elif ("jpg"  in self.fileName):
            self.result = test.predict(self.fileName)
            if self.result == True:
                self.ui.result.setText("正常")
                # print("正常")
            else:
                # print("异常")
                self.ui.result.setText("异常")
        else:
            print("请选择文件")

    def openFile(self):
        # self.fileName = tkFileDialog.askopenfilename(self, '选择图片', 'c:\\', 'Image files(*.jpg *.dic *.dicom)')
        self.fileName,_ = QtWidgets.QFileDialog.getOpenFileName(self, '选择图片')
        if (self.fileName != "") & ("jpg" not in self.fileName):
            self.file1 = dicom.read_file(self.fileName).pixel_array
            self.img = Image.fromarray(self.file1)

            number = int(self.fileName[-3:])
            self.preFileName = self.fileName[:-3] + str(number - 1).zfill(3)
            self.postFileName = self.fileName[:-3] + str(number + 1).zfill(3)
            self.preFile = dicom.read_file(self.preFileName).pixel_array
            self.postFile = dicom.read_file(self.postFileName).pixel_array

            # Image.fromarray(preprocess.function_z(self.file1)).show()
            self.preimg = Image.fromarray(self.preFile)
            self.postimg = Image.fromarray(self.postFile)

            self.show = Image.fromarray(preprocess.function_z(self.file1)).resize((self.ui.label_4.width(),self.ui.label_4.height()))
            self.show.save("./Image/show.jpg")
            pix = QtGui.QPixmap("./Image/show.jpg")
            self.ui.label_4.setPixmap(pix)
        elif "jpg"  in self.fileName:
            self.show = Image.open(self.fileName).resize((self.ui.label_4.width(),self.ui.label_4.height()))
            self.show.save("./Image/show.jpg")
            pix = QtGui.QPixmap("./Image/show.jpg")
            self.ui.label_4.setPixmap(pix)
        else:
            print("没有选择文件")

    def getseed(self):
        if (self.fileName != "") & ("jpg" not in self.fileName):
            self.roi = self.img
            self.preRoi =self.preimg
            self.postRoi = self.postimg

            roi_pix = np.array(self.roi)
            preRoi_pix = np.array(self.preRoi)
            postRoi_pix = np.array(self.postRoi)

            # 获取所有的SUV值
            suv_arr = preprocess.getASuv(self.fileName, roi_pix)

            preSuv_arr = preprocess.getASuv(self.preFileName, preRoi_pix)
            postSuv_arr = preprocess.getASuv(self.postFileName, postRoi_pix)

            # 获取 SUVmax
            self.suv_max = np.max(suv_arr)
            suv_max = self.suv_max
            re = np.where(suv_max == suv_arr)
            suv_max_x = re[0][0]
            suv_max_y = re[1][0]

            def getSeed(re3):
                return re3.min(), re3.max()

            x = suv_arr[suv_max_x]
            re1 = np.where(x > suv_max * 0.4)
            seed1_y, seed2_y = getSeed(re1[0])
            y = suv_arr[:, suv_max_y]
            re2 = np.where(y > suv_max * 0.4)
            seed3_x, seed4_x = getSeed(re2[0])

            fig = plt.figure()
            ax = fig.add_subplot(1, 2, 1)
            ax1 = fig.add_subplot(1, 2, 2)
            ax.plot(x)
            ax1.plot(y)

            # seed1 = (suv_max_x, seed1_y)
            # seed2 = (suv_max_x, seed2_y)
            # seed3 = (seed3_x, suv_max_y)
            # seed4 = (seed4_x, suv_max_y)
            #
            # print(suv_max_x,suv_max_y,seed1,seed2,seed3,seed4)

            # plt.show()
            # 初始化 C 和 seta
            setap = np.zeros(roi_pix.shape)
            setap[suv_max_x][seed1_y] = 1
            setap[suv_max_x][seed2_y] = 1
            setap[seed3_x][suv_max_y] = 1
            setap[seed4_x][suv_max_y] = 1

            x = roi_pix.shape[0]
            y = roi_pix.shape[1]

            Cp = setap
            Cp[0] = 2
            Cp[x - 1] = 2
            Cp[:, 0] = 2
            Cp[:, y - 1] = 2

            Cp = Cp.astype(np.uint8)

            setap[0] = 1
            setap[x - 1] = 1
            setap[:, 0] = 1
            setap[:, y - 1] = 1

            # print(setap)
            # re1 = np.where(setap ==1)
            # print(re1)

            # 初始化标签
            # def getCp(roi_pix):
            #     Cp = roi_pix
            #     for x in range(0,(Cp.shape)[0]):
            #         for y in range(0,(Cp.shape)[1]):
            #             if Cp[x][y] == 0:
            #                 Cp[x][y] = 2
            #             else:
            #                 Cp[x][y] = 1
            #     return Cp



            Cp1 = Cp
            Cq1 = np.zeros(roi_pix.shape).astype(np.uint8)
            Cq2 = np.zeros(roi_pix.shape).astype(np.uint8)

            setap = setap.astype(np.float32)
            # print(setap)
            setap1 = setap
            setaq = np.zeros(preRoi_pix.shape).astype(np.float32)
            setaq2 = np.zeros(postRoi_pix.shape).astype(np.float32)

            T = 10 ** (-6)
            seta = T + 1

            def functionWp(px, py):
                a = 0.
                b = 0.
                c = 0.
                for x in range(px - 1, px + 1):
                    for y in range(py - 1, py + 1):
                        a += (preSuv_arr[x][y] - suv_arr[px][py]) ** 2
                        b += (postSuv_arr[x][y] - suv_arr[px][py]) ** 2
                        c += (suv_arr[x][y] - suv_arr[px][py]) ** 2
                d = ((a + b + c) / 26) ** 0.5
                Wp = 1 / (1 + d)

                return Wp

            def functionG(px, py, x):
                a = functionWp(px, py) * x
                b = abs(suv_max)
                Gx = 1 - (a / b)
                # print(Gx)
                return Gx

            while seta > T:
                # print(seta)
                for x in range(1, (roi_pix.shape)[0] - 1):
                    for y in range(1, (roi_pix.shape)[1] - 1):
                        Cp1[x][y] = Cp[x][y]
                        setap1[x][y] = setap[x][y]
                        for px in range(x - 1, x + 1):
                            for py in range(y - 1, y + 1):
                                a = (functionG(px, py, abs(suv_arr[x][y] - preSuv_arr[px][py])) * setaq[px][py])
                                if a > setap[x][y]:
                                    Cp1[x][y] = Cq1[px][py]
                                    setap1[x][y] = a

                        for px in range(x - 1, x + 1):
                            for py in range(y - 1, y + 1):
                                b = (functionG(px, py, abs(suv_arr[x][y] - postSuv_arr[px][py])) * setaq2[px][py])
                                if b > setap[x][y]:
                                    Cp1[x][y] = Cq2[px][py]
                                    setap1[x][y] = b
                        for px in range(x - 1, x + 1):
                            for py in range(y - 1, y + 1):
                                c = (functionG(px, py, abs(suv_arr[x][y] - suv_arr[px][py])) * setap[px][py])
                                if c > setap[x][y]:
                                    Cp1[x][y] = Cp[px][py]
                                    setap1[x][y] = c

                seta = ((Cp1 - Cp) ** 2).sum()
                Cp = Cp1
                setap = setap1

            # Cp1 = Cp1.astype(np.uint8)



            ca_result_show = Image.fromarray(preprocess.function_z(Cp1)).resize((self.ui.label_5.width(),self.ui.label_5.height()))
            ca_result_show.save("./Image/ca_result.jpg")
            pix = QtGui.QPixmap("./Image/ca_result.jpg")
            self.ui.label_5.setPixmap(pix)
            # self.image3 = ImageTk.PhotoImage(result_show)
            # self.Canvas3.create_image(0, 0, image=self.image3, anchor=tkinter.NW)
            # self.variab1.set('')
            # Image.fromarray(preprocess.function_z(Cp1)).show()
            # return Cp1
        else:
           print("请选择文件")



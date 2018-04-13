from tkinter import *
from graduation.page.client import login
from PyQt5 import QtWidgets,QtGui
from graduation.page.client import mainWindow
# root = Tk()
# root.title('PET/CT图像分类系统')
# loginPage.LoginPage(root)
# root.mainloop()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    dialog = login.Login()


    if dialog.exec_():
        MainWindow = QtWidgets.QMainWindow()
        window = mainWindow.firstWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        print("主界面打开失败")
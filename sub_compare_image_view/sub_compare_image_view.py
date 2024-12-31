from ui.sub_ui import Ui_MainWindow
import sys, os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QLabel, QHeaderView, QWidget, QShortcut
from PyQt5.QtGui import QIcon, QImage, QPixmap, QKeySequence, QStandardItem
from PyQt5.QtCore import Qt, QEvent, QSize, QPoint
from PIL import Image

one_pic = ['C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/000_test_A_10_Lux_.jpg']
two_pic = ['C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/000_test_A_10_Lux_.jpg', 'C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/001_test_A_10_Lux_.jpg']
three_pic = ['C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/000_test_A_10_Lux_.jpg', 'C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/001_test_A_10_Lux_.jpg', 'C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/002_test_A_10_Lux_.jpg']

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.images = []     # 初始化图片列表
        self.init_ui()       # 调用初始化界面组件的方法
        self.showMaximized() # 设置窗口为最大化模式
        # 创建快捷键，按住Esc键退出整个界面
        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut_esc.activated.connect(self.close)
        
    def init_ui(self):
        # 设置主界面图标以及标题
        # icon_path = os.path.join(os.path.dirname(__file__), "images", "viewer.ico")
        # self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("HiViewer_V1.0")
        # 设置窗口为全屏模式
        # self.showFullScreen()

        # 导入字体，设置显示的字体样式
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "霞鹜文楷.ttf")  # 字体文件路径
        font_db = QtGui.QFontDatabase()
        font_id = font_db.addApplicationFont(font_path)
        font_family = font_db.applicationFontFamilies(font_id)[0]
        custom_font = QtGui.QFont(font_family, 12)  # 设置字体大小为12，可以根据需要调整

        font_path1 = os.path.join(os.path.dirname(__file__), "fonts", "波纹乖乖体.ttf")  # 字体文件路径
        font_id1 = font_db.addApplicationFont(font_path1)
        font_family1 = font_db.applicationFontFamilies(font_id1)[0]
        custom_font1 = QtGui.QFont(font_family1, 10)  # 设置字体大小为12，可以根据需要调整        

        font_path2 = os.path.join(os.path.dirname(__file__), "fonts", "萌趣果冻体.ttf")  # 字体文件路径
        font_id2 = font_db.addApplicationFont(font_path2)
        font_family2 = font_db.applicationFontFamilies(font_id2)[0]
        custom_font2 = QtGui.QFont(font_family2, 12)  # 设置字体大小为12，可以根据需要调整

        """窗口组件概览
        第一排, self.label_0, self.comboBox_1, self.comboBox_2, self.checkBox_1, self.checkBox_2, self.checkBox_3
        第二排, self.tableWidget_medium
        第三排, self.label_bottom
        """

        # 初始化第一排组件
        self.label_0.setStyleSheet("background-color: lightblue;text-align: center; border-radius:10px;")
        self.label_0.setText(" 提示: 鼠标左键拖动图像, 滚轮控制放大/缩小; 按住Ctrl或者鼠标右键操作单独图像 ")  # 根据需要设置标签的文本
        self.label_0.setFont(custom_font)  # 应用自定义字体


        self.checkBox_1.setText("Exif信息")
        self.checkBox_1.setFont(custom_font)  
        self.checkBox_2.setText("直方图信息")
        self.checkBox_2.setFont(custom_font)  
        self.checkBox_3.setText("AI提示看图")
        self.checkBox_3.setFont(custom_font)  

        # 初始化第二排组件
        header = self.tableWidget_medium.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { background-color: lightblue;text-align: center; border-radius:10px;}")
        header.setFont(custom_font) # 设置字体  
        self.tableWidget_medium.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_medium.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_medium.verticalHeader().setVisible(False)
        self.tableWidget_medium.verticalHeader().setDefaultSectionSize(0)   

        # 注意: 为了使单元格的颜色不变，设置样式表
        self.tableWidget_medium.setStyleSheet("""
            QTableWidget::item {
                background-color: rgb(127, 127, 127);  /* 设置单元格背景颜色为RGB(127, 127, 127) */
            }
            QTableWidget::item:selected {
                background-color: rgb(127, 127, 127);  /* 或者设置为其他颜色，例如 white */
            }
        """) 
        
        self.set_images(three_pic)

        # 初始化第三排组件
        self.label_bottom.setStyleSheet("background-color: lightblue;text-align: center; border-radius:10px;")
        self.label_bottom.setText(" 这是一个AI看图信息提示栏 ")  # 根据需要设置标签的文本
        self.label_bottom.setFont(custom_font)  # 应用自定义字体

    def set_images(self, image_paths):
        # 清空现有的表格内容
        self.images.clear()
        self.tableWidget_medium.clearContents()
        self.tableWidget_medium.setColumnCount(len(image_paths))
        self.tableWidget_medium.setRowCount(1)  # 设置行数为1

        folder_names = [os.path.basename(os.path.dirname(path)) for path in image_paths]
        self.tableWidget_medium.setHorizontalHeaderLabels(folder_names)  # 设置列名为文件夹名

        for index, path in enumerate(image_paths):
            if not os.path.exists(path):  # 检查图片路径是否有效
                print(f"图片路径无效: {path}")
                continue
            pixmap = QPixmap(path)
            if pixmap.isNull():  # 检查图片是否加载成功
                print(f"图片加载失败: {path}")
                continue
            
            # 确保在这里设置 original_pixmap
            label = QLabel(self)
            label.original_pixmap = pixmap  # 设置原始图片
            label.setPixmap(pixmap.scaled(QSize(pixmap.width()//5, pixmap.height()//5), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation))
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(False)  # 不自动缩放到标签大小
            label.is_moving = False
            label.start_pos = QPoint()
            label.setMouseTracking(True)  # 启用鼠标跟踪
            self.tableWidget_medium.setCellWidget(0, index, label)
            self.images.append(label)

    def wheelEvent(self, event: QEvent):
        delta = event.angleDelta().y()
        zoom_factor = 1.2 if delta > 0 else 1/1.2
        max_zoom_factor = 6.0  # 设置最大缩放比例
        min_zoom_factor = 0.1  # 设置最小缩放比例

        for label in self.images:
            current_pixmap = label.pixmap()
            if current_pixmap is not None:
                current_width = current_pixmap.width()
                current_height = current_pixmap.height()
                new_width = int(current_width * zoom_factor)
                new_height = int(current_height * zoom_factor)

                # 计算当前缩放比例
                current_zoom_factor = current_width / label.original_pixmap.width()

                # 限制缩放比例在最小和最大之间
                if current_zoom_factor * zoom_factor > max_zoom_factor or current_zoom_factor * zoom_factor < min_zoom_factor:
                    continue

                pixmap = label.original_pixmap.scaled(QSize(new_width, new_height), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event: QEvent):
        for label in self.images:
            if label.geometry().contains(event.pos()):
                label.is_moving = True
                label.start_pos = event.pos()
                label.start_pixmap_pos = label.pos()
                break

    def mouseMoveEvent(self, event: QEvent):
        if any(label.is_moving for label in self.images):
            for label in self.images:
                if label.is_moving:
                    current_pos = label.start_pixmap_pos + (event.pos() - label.start_pos)
                    label.move(current_pos)
                    label.start_pos = event.pos()
                    break

    def mouseReleaseEvent(self, event: QEvent):
        for label in self.images:
            label.is_moving = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
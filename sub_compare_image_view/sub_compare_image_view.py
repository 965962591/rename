from ui.sub_ui import Ui_MainWindow
import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QLabel, QHeaderView, QWidget,
    QShortcut, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QImage, QPixmap, QKeySequence, QFontDatabase, QFont, QPainter, QCursor
from PyQt5.QtCore import Qt, QEvent, QSize, QPoint
from PIL import Image
from fractions import Fraction

import matplotlib.pyplot as plt
import io

one_pic = ['C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/000_test_A_10_Lux_.jpg']
two_pic = ['C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/000_test_A_10_Lux_.jpg', 'C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/001_test_A_10_Lux_.jpg']
three_pic = ['C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/000_test_A_10_Lux_.jpg', 'C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/001_test_A_10_Lux_.jpg', 'C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/002_test_A_10_Lux_.jpg']

class MyGraphicsView(QGraphicsView):
    def __init__(self, scene, exif_text=None, *args, **kwargs):
        super(MyGraphicsView, self).__init__(scene, *args, **kwargs)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.exif_text = exif_text  # 存储 EXIF 信息
        self.show_exif = True if exif_text else False  # 控制 EXIF 显示

        self.histogram = None  # 存储直方图数据
        self.show_histogram = False  # 控制直方图显示

        # 添加 QLabel 显示 EXIF 信息
        self.exif_label = QLabel(self)
        self.exif_label.setText(self.exif_text if self.exif_text else "")
        # 设置仅文本颜色，不使用背景颜色
        self.exif_label.setStyleSheet("color: red; background-color: transparent;")
        self.exif_label.setFont(QFont("Arial", 10))
        self.exif_label.move(5, 5)  # 固定在左上角，适当调整偏移量
        self.exif_label.setVisible(self.show_exif)
        self.exif_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # 让标签不拦截鼠标事件

        # 添加 QLabel 显示直方图
        self.histogram_label = QLabel(self)
        self.histogram_label.setStyleSheet("border: 1px solid black;")
        self.histogram_label.setVisible(self.show_histogram)
        self.histogram_label.setAttribute(Qt.WA_TransparentForMouseEvents)

    def set_histogram_data(self, histogram):
        if histogram is None:
            self.histogram_label.setText("无直方图数据")
            return
        # 使用 matplotlib 生成直方图图像
        try:
            plt.figure(figsize=(4, 3), dpi=50, facecolor='none', edgecolor='none')  # 设置背景透明
            ax = plt.gca()
            # 计算相对频率
            total_pixels = sum(histogram)
            relative_frequency = [count / total_pixels for count in histogram]
            # 绘制步进图以保证直方图连续
            ax.plot(range(len(relative_frequency)), relative_frequency, color='gray', linewidth=1)
            ax.fill_between(range(len(relative_frequency)), relative_frequency, color='gray', alpha=0.7)
            # ax.set_title('亮度直方图', fontsize=10)
            # ax.set_xlabel('亮度', fontsize=8)
            # ax.set_ylabel('频率', fontsize=8)
            ax.set_xlim(0, 255)
            ax.set_ylim(0, max(relative_frequency)*1.1)
            ax.yaxis.set_visible(False)  # 隐藏 Y 轴
            ax.xaxis.set_tick_params(labelsize=8)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='PNG', transparent=True, bbox_inches='tight', pad_inches=0)
            buf.seek(0)
            plt.close()

            histogram_pixmap = QPixmap()
            histogram_pixmap.loadFromData(buf.getvalue(), 'PNG')
            buf.close()

            self.histogram_label.setPixmap(histogram_pixmap)
        except Exception as e:
            print(f"生成直方图图像失败: {e}")
            self.histogram_label.setText("无法生成直方图")

    def set_histogram_visibility(self, visible: bool):
        self.show_histogram = visible
        self.histogram_label.setVisible(visible)

    def wheelEvent(self, event: QEvent):
        # 将事件传递给父级窗口处理
        self.parent().wheelEvent(event)

    def set_exif_visibility(self, visible: bool):
        self.show_exif = visible
        self.exif_label.setVisible(visible)

    def resizeEvent(self, event):
        super(MyGraphicsView, self).resizeEvent(event)
        self.exif_label.move(5, 5)  # 保持在左上角
        self.histogram_label.move(5, 50)  # 调整直方图的位置

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.images = []            # 初始化图片列表
        self.graphics_views = []    # 确保在这里初始化
        self.pixmap_items = []      # 存储每个图片项
        self.exif_texts = []        # 存储每个视图的 EXIF 信息
        self.histograms = []        # 存储每个视图的直方图

        self.init_ui()              # 调用初始化界面组件的方法
        self.showMaximized()        # 设置窗口为最大化模式

        # 创建快捷键，按住Esc键退出整个界面
        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut_esc.activated.connect(self.close)
        
        # 添加Ctrl+A和Ctrl+D快捷键
        self.shortcut_rotate_left = QShortcut(QKeySequence("Ctrl+A"), self)
        self.shortcut_rotate_left.activated.connect(self.rotate_left)

        self.shortcut_rotate_right = QShortcut(QKeySequence("Ctrl+D"), self)
        self.shortcut_rotate_right.activated.connect(self.rotate_right)

        # 连接复选框信号到槽函数
        self.checkBox_1.stateChanged.connect(self.toggle_exif_info)
        self.checkBox_2.stateChanged.connect(self.toggle_histogram_info)  # 新增

    def init_ui(self):
        # 设置主界面图标以及标题
        # icon_path = os.path.join(os.path.dirname(__file__), "images", "viewer.ico")
        # self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("HiViewer_V1.0")
        # 设置窗口为全屏模式
        # self.showFullScreen()

        # 导入字体，设置显示的字体样式
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "霞鹜文楷.ttf")  # 字体文件路径
        font_db = QFontDatabase()
        font_id = font_db.addApplicationFont(font_path)
        font_family = font_db.applicationFontFamilies(font_id)[0]
        custom_font = QFont(font_family, 12)  # 设置字体大小为12，可以根据需要调整

        font_path1 = os.path.join(os.path.dirname(__file__), "fonts", "波纹乖乖体.ttf")  # 字体文件路径
        font_id1 = font_db.addApplicationFont(font_path1)
        font_family1 = font_db.applicationFontFamilies(font_id1)[0]
        custom_font1 = QFont(font_family1, 10)  # 设置字体大小为10，可以根据需要调整        

        font_path2 = os.path.join(os.path.dirname(__file__), "fonts", "萌趣果冻体.ttf")  # 字体文件路径
        font_id2 = font_db.addApplicationFont(font_path2)
        font_family2 = font_db.applicationFontFamilies(font_id2)[0]
        custom_font2 = QFont(font_family2, 12)  # 设置字体大小为12，可以根据需要调整

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

        # 连接复选框信号到槽函数
        self.checkBox_1.stateChanged.connect(self.toggle_exif_info)

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
        self.images.clear()
        self.graphics_views.clear()    # 清理之前的视图列表
        self.pixmap_items.clear()      # 清空之前的图片项
        self.exif_texts.clear()        # 清空之前的 EXIF 信息
        self.histograms.clear()        # 清空之前的直方图信息
        self.tableWidget_medium.clearContents()
        self.tableWidget_medium.setColumnCount(len(image_paths))
        self.tableWidget_medium.setRowCount(1)

        folder_names = [os.path.basename(os.path.dirname(path)) for path in image_paths]
        self.tableWidget_medium.setHorizontalHeaderLabels(folder_names)

        for index, path in enumerate(image_paths):
            if not os.path.exists(path):
                print(f"图片路径无效: {path}")
                self.exif_texts.append(None)
                self.histograms.append(None)
                continue
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"图片加载失败: {path}")
                self.exif_texts.append(None)
                self.histograms.append(None)
                continue

            scene = QGraphicsScene(self)
            pixmap_item = QGraphicsPixmapItem(pixmap)
            # 设置变换原点为图片中心
            pixmap_item.setTransformOriginPoint(pixmap.rect().center())
            scene.addItem(pixmap_item)
            self.pixmap_items.append(pixmap_item)  # 存储图片项

            # 获取 EXIF 信息
            exif_info = self.get_exif_info(path)
            if not exif_info:
                exif_info = "无EXIF信息"
            self.exif_texts.append(exif_info)

            # 计算亮度直方图
            histogram = self.calculate_brightness_histogram(path)
            self.histograms.append(histogram)

            view = MyGraphicsView(scene, exif_info, self)
            # 设置初始缩放比例
            initial_scale = 0.5  # 例如，缩小到50%
            view.scale(initial_scale, initial_scale)
            
            # 根据复选框状态设置 EXIF 信息和直方图的可见性
            view.set_exif_visibility(self.checkBox_1.isChecked())
            view.set_histogram_visibility(self.checkBox_2.isChecked())

            # 设置直方图数据
            if self.histograms[index]:
                view.set_histogram_data(self.histograms[index])
            else:
                view.set_histogram_data(None)

            self.tableWidget_medium.setCellWidget(0, index, view)
            self.graphics_views.append(view)

    def toggle_exif_info(self, state):
        print(f"切换 EXIF 信息: {'显示' if state == Qt.Checked else '隐藏'}")
        for view, exif_text in zip(self.graphics_views, self.exif_texts):
            if exif_text:
                view.set_exif_visibility(state == Qt.Checked)

    def toggle_histogram_info(self, state):
        print(f"切换直方图信息: {'显示' if state == Qt.Checked else '隐藏'}")
        for view, histogram in zip(self.graphics_views, self.histograms):
            if histogram:
                view.set_histogram_visibility(state == Qt.Checked)

    def calculate_brightness_histogram(self, path):
        try:
            image = Image.open(path).convert('L')  # 转换为灰度图
            histogram = image.histogram()
            # 只保留0-255的灰度值
            histogram = histogram[:256]
            return histogram
        except Exception as e:
            print(f"计算直方图失败: {path}\n错误: {e}")
            return None

    def get_exif_info(self, path):
        # 定义 EXIF 标签的中文映射
        exif_tags_cn = {
            'DateTime': '时间',
            'Model': '机型',
            'ExposureTime': '曝光时间',
            'FNumber': '光圈',
            'ISOSpeedRatings': 'ISO'
        }
        
        if not os.path.exists(path):
            return f"图片路径无效: {path}"
        try:
            image = Image.open(path)
            exif_data = image._getexif()
            if exif_data:
                exif = {
                    Image.ExifTags.TAGS.get(tag, tag): value
                    for tag, value in exif_data.items()
                }
                exif_info_list = []
                for k, v in exif.items():
                    if k in exif_tags_cn:  # 使用中文标签
                        k_cn = exif_tags_cn[k]
                        if k == 'ExposureTime':
                            # 格式化 ExposureTime 为分数形式
                            exposure_time = "未知格式"  # 默认值
                            if isinstance(v, tuple) and len(v) == 2 and v[1] != 0:
                                exposure_time = f"{v[0]}/{v[1]}"
                            elif isinstance(v, (int, float)):
                                try:
                                    # 将 limit_denominator 设置为 50 以获得更合理的分数表示
                                    fraction = Fraction(v).limit_denominator(50)
                                    exposure_time = f"{fraction.numerator}/{fraction.denominator}"
                                except Exception:
                                    exposure_time = str(v)
                            elif hasattr(v, 'numerator') and hasattr(v, 'denominator'):
                                # 处理类似 Exif.Ratio 的类型
                                try:
                                    fraction = Fraction(v.numerator, v.denominator).limit_denominator(50)
                                    exposure_time = f"{fraction.numerator}/{fraction.denominator}"
                                except Exception:
                                    exposure_time = "未知格式"
                            elif isinstance(v, str):
                                # 尝试从字符串中解析分数
                                try:
                                    fraction = Fraction(v).limit_denominator(50)
                                    exposure_time = f"{fraction.numerator}/{fraction.denominator}"
                                except Exception:
                                    exposure_time = v
                            exif_info_list.append(f"{k_cn}: {exposure_time}")
                        else:
                            exif_info_list.append(f"{k_cn}: {v}")
                exif_info = "\n".join(exif_info_list)
            else:
                exif_info = "无EXIF信息"
            return exif_info
        except Exception as e:
            return f"无法读取EXIF信息: {path}\n错误: {e}"

    def mousePressEvent(self, event: QEvent):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPos()

    def mouseMoveEvent(self, event: QEvent):
        if event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self.start_pos
            self.start_pos = event.globalPos()  # 更新起始位置

            for view in self.graphics_views:
                # 直接移动视图的场景位置，而不是滚动条
                view.horizontalScrollBar().setValue(view.horizontalScrollBar().value() - delta.x())
                view.verticalScrollBar().setValue(view.verticalScrollBar().value() - delta.y())

    def mouseReleaseEvent(self, event: QEvent):
        if event.button() == Qt.LeftButton:
            print("Mouse release detected")

    def wheelEvent(self, event: QEvent):
        zoom_factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
        if event.modifiers() & Qt.ControlModifier:
            # 遍历 graphics_views 找到鼠标所在的 MyGraphicsView
            pos = self.mapFromGlobal(event.globalPos())
            for view in self.graphics_views:
                # 使用 mapFromParent 将全局坐标转换为 view 的本地坐标
                local_pos = view.mapFromParent(self.mapFromGlobal(event.globalPos()))
                if view.rect().contains(local_pos):
                    self.zoom_view(view, zoom_factor)
                    break
        else:
            # 缩放所有图片
            for view in self.graphics_views:
                self.zoom_view(view, zoom_factor)

    def zoom_view(self, view, zoom_factor):
        current_scale = view.transform().m11()
        min_scale = 0.1
        max_scale = 10.0
        new_scale = current_scale * zoom_factor

        if min_scale <= new_scale <= max_scale:
            center = view.mapToScene(view.viewport().rect().center())
            view.scale(zoom_factor, zoom_factor)
            view.centerOn(center)

    def rotate_left(self):
        self.rotate_image(-90)

    def rotate_right(self):
        self.rotate_image(90)

    def rotate_image(self, angle):
        # 获取鼠标的全局位置
        cursor_pos = QCursor.pos()
        # 将全局位置转换为窗口内的位置
        pos = self.mapFromGlobal(cursor_pos)
        
        for view in self.graphics_views:
            # 使用 mapFromParent 将全局坐标转换为 view 的本地坐标
            local_pos = view.mapFromParent(pos)
            if view.rect().contains(local_pos):
                items = view.items(local_pos)
                if items:
                    pixmap_item = items[0]
                    # 设置旋转围绕中心
                    pixmap_item.setRotation(pixmap_item.rotation() + angle)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
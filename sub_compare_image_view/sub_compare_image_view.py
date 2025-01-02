from ui.sub_ui import Ui_MainWindow
import sys, os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidgetItem, QLabel, QHeaderView, QWidget,
    QShortcut, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout,
    QMessageBox
)
from PyQt5.QtGui import QIcon, QImage, QPixmap, QKeySequence, QFontDatabase, QFont, QPainter, QCursor, QTransform
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QPoint, QSize
from PIL import Image
from fractions import Fraction
import piexif
import matplotlib.pyplot as plt
import io

one_pic = ["C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/000_test_A_10_Lux_.jpg"]
two_pic = ["C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/1st_IMG_20241210_102946.jpg", "C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/4th_IMG_20241210_035634.jpg"]
three_pic = ["C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/1st_IMG_20241210_102946.jpg", "C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/001_test_A_10_Lux_.jpg", "C:/Users/chenyang3/Desktop/rename/sub_compare_image_view/test/002_test_A_10_Lux_.jpg"]
class ImageTransform:
    """图片旋转exif信息调整类"""
    # 定义EXIF方向值对应的QTransform变换
    _ORIENTATION_TRANSFORMS = {
        1: QTransform(),  # 0度 - 正常
        2: QTransform().scale(-1, 1),  # 水平翻转
        3: QTransform().rotate(180),  # 180度
        4: QTransform().scale(1, -1),  # 垂直翻转
        5: QTransform().rotate(90).scale(-1, 1),  # 顺时针90度+水平翻转
        6: QTransform().rotate(90),  # 顺时针90度
        7: QTransform().rotate(-90).scale(-1, 1),  # 逆时针90度+水平翻转
        8: QTransform().rotate(-90)  # 逆时针90度
    }
    
    @classmethod
    def auto_rotate_image(cls, icon_path: str) -> QIcon:
            
        try:
            # 获取EXIF方向信息
            orientation = 1  # 默认方向
            try:
                img = Image.open(icon_path)
                exif_dict = piexif.load(img.info.get('exif', b''))
                if '0th' in exif_dict and piexif.ImageIFD.Orientation in exif_dict['0th']:
                    orientation = exif_dict['0th'][piexif.ImageIFD.Orientation]
                img.close()  # 确保关闭文件
            except Exception as e:
                print(f"读取EXIF信息失败: {str(e)}")
                pass
            
            # 创建QPixmap
            pixmap = QPixmap(icon_path)
            
            # 应用方向变换
            transform = cls._ORIENTATION_TRANSFORMS.get(orientation, QTransform())
            if not transform.isIdentity():  # 只在需要变换时执行
                pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)
            
            
            return pixmap
            
        except Exception as e:
            print(f"处理图标失败 {icon_path}: {str(e)}")
            return QIcon()

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

        self.pixmap_items = []  # 初始化 pixmap_items 列表
        print("Initialized MyGraphicsView with empty pixmap_items")

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
        self.histogram_label.setStyleSheet("border: none;")  # 去除边框
        self.histogram_label.move(5, 5 + self.exif_label.height() + 5)  # 位置在 exif_label 下方
        self.histogram_label.setVisible(self.show_histogram)
        self.histogram_label.setFixedSize(150, 100)  # 根据需要调整大小
        self.histogram_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # 不拦截鼠标事件
    def set_histogram_data(self, histogram):
        if histogram is None:
            self.histogram_label.setText("无直方图数据")
            return
        # 使用 matplotlib 生成直方图图像
        try:
            plt.figure(figsize=(3, 2), dpi=100, facecolor='none', edgecolor='none')  # 设置背景透明
            ax = plt.gca()
            # 计算相对频率
            total_pixels = sum(histogram)
            relative_frequency = [count / total_pixels for count in histogram]
            # 绘制步进图以保证直方图连续
            # ax.plot(range(len(relative_frequency)), relative_frequency, color='gray', linewidth=1)
            # ax.fill_between(range(len(relative_frequency)), relative_frequency, color='gray', alpha=0.7)
            ax.plot(range(len(relative_frequency)), relative_frequency, color='skyblue', linewidth=1)
            ax.fill_between(range(len(relative_frequency)), relative_frequency, color='skyblue', alpha=0.7)            
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

            # 缩放直方图图像以适应 QLabel
            self.histogram_label.setPixmap(histogram_pixmap.scaled(
                self.histogram_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
        # 根据 exif_label 的高度动态设置 histogram_label 的位置
        exif_label_height = self.exif_label.height()
        padding = 5  # 两个标签之间的间隔
        self.histogram_label.move(5, 5 + exif_label_height + padding)

class SubMainWindow(QMainWindow, Ui_MainWindow):
    closed = pyqtSignal()
    def __init__(self, images_path_list, parent=None):
        super(SubMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.images_path_list = images_path_list     # 初始化图片列表

        self.images = []            # 初始化图片列表
        self.graphics_views = []  # 确保在这里初始化
        
        
        self.pixmap_items = []    # 新增：存储每个图片项
        self.exif_texts = []        # 存储每个视图的 EXIF 信息
        self.histograms = []        # 存储每个视图的直方图

        self.original_pixmaps = []  # 缓存原始图片的 QPixmap 对象

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

        # 添加q和w快捷键，设置为应用程序级别
        self.shortcut_q = QShortcut(QKeySequence("q"), self)
        self.shortcut_q.setContext(Qt.ApplicationShortcut)
        self.shortcut_q.activated.connect(lambda: self.handle_overlay('q'))

        self.shortcut_w = QShortcut(QKeySequence("w"), self)
        self.shortcut_w.setContext(Qt.ApplicationShortcut)
        self.shortcut_w.activated.connect(lambda: self.handle_overlay('w'))

        # 连接复选框信号到槽函数
        self.checkBox_1.stateChanged.connect(self.toggle_exif_info)
        self.checkBox_2.stateChanged.connect(self.toggle_histogram_info)  # 新增

    def init_ui(self):
        
        # 设置主界面图标以及标题
        icon_path = os.path.join(os.path.dirname(__file__), "images", "viewer.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("HiViewer_V1.0")

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
        # 设置传入的图片路径列表
        self.set_images(self.images_path_list)

        # 初始化第三排组件
        self.label_bottom.setStyleSheet("background-color: lightblue;text-align: center; border-radius:10px;")
        self.label_bottom.setText(" 这是一个AI看图信息提示栏 ")  # 根据需要设置标签的文本
        self.label_bottom.setFont(custom_font)  # 应用自定义字体
    def set_images(self, image_paths):
        self.images.clear()
        self.graphics_views.clear()
        self.pixmap_items.clear()
        self.exif_texts.clear()
        self.histograms.clear()
        self.original_pixmaps.clear()
        self.tableWidget_medium.clearContents()
        self.tableWidget_medium.setColumnCount(len(image_paths))
        self.tableWidget_medium.setRowCount(1)

        folder_names = [os.path.basename(os.path.dirname(path)) for path in image_paths]
        self.tableWidget_medium.setHorizontalHeaderLabels(folder_names)

        base_width, base_height = self.get_base_size(image_paths)

        for index, path in enumerate(image_paths):
            if not os.path.exists(path):
                print(f"图片路径无效: {path}")
                self.images.append(path)
                self.exif_texts.append(None)
                self.histograms.append(None)
                self.original_pixmaps.append(None)
                continue

            pixmap = ImageTransform.auto_rotate_image(path)

            if pixmap.isNull():
                print(f"图片加载失败: {path}")
                self.images.append(path)
                self.exif_texts.append(None)
                self.histograms.append(None)
                self.original_pixmaps.append(None)
                continue

            # 计算缩放倍率
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
            scale_factor = min(base_width / pixmap_width, base_height / pixmap_height)
            new_width = int(pixmap_width * scale_factor)
            new_height = int(pixmap_height * scale_factor)
            scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            self.images.append(path)
            scene = QGraphicsScene(self)
            pixmap_item = QGraphicsPixmapItem(scaled_pixmap)
            pixmap_item.setTransformOriginPoint(scaled_pixmap.rect().center())
            scene.addItem(pixmap_item)

            view = MyGraphicsView(scene, self.get_exif_info(path), self)
            view.pixmap_items.append(pixmap_item)
            self.graphics_views.append(view)

            exif_info = self.get_exif_info(path)
            if not exif_info:
                exif_info = "无EXIF信息"
            self.exif_texts.append(exif_info)

            histogram = self.calculate_brightness_histogram(path)
            self.histograms.append(histogram)

            initial_scale = 1.0  # 已经根据基准尺寸缩放，无需进一步缩放
            view.scale(initial_scale, initial_scale)

            view.set_exif_visibility(self.checkBox_1.isChecked())
            view.set_histogram_visibility(self.checkBox_2.isChecked())

            if self.histograms[index]:
                view.set_histogram_data(self.histograms[index])
            else:
                view.set_histogram_data(None)

            self.tableWidget_medium.setCellWidget(0, index, view)
            self.original_pixmaps.append(scaled_pixmap)

    def get_base_size(self, image_paths):
        """
        获取基准尺寸，选择第一张图片的尺寸作为基准。
        如果第一张图片无效，则选择下一张有效图片。
        """
        for path in image_paths:
            if os.path.exists(path):
                pixmap = ImageTransform.auto_rotate_image(path)
                if not pixmap.isNull():
                    return pixmap.width(), pixmap.height()
        # 如果所有图片都无效，设定默认尺寸
        return 800, 600

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
    def pic_size(self, path):
            # 获取图片尺寸
        image = Image.open(path)
        width, height = image.size
        file_size = os.path.getsize(path)  # 文件大小（字节）
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 ** 2:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size / (1024 ** 2):.2f} MB"
        exif_size_info = f"图片大小: {size_str}\n图片尺寸: {width} x {height}"
        return exif_size_info
    
    def get_exif_info(self, path):
        exif_size_info = self.pic_size(path)
        try:
            image = Image.open(path)
            exif_data = image._getexif()
            if exif_data:
                exif = {
                    Image.ExifTags.TAGS.get(tag, tag): value
                    for tag, value in exif_data.items()
                }
                exif_tags_cn = {
                    "Make": "品牌",
                    "Model": "型号",
                    "DeviceModel": "设备型号",
                    "ExposureTime": "曝光时间",
                    "FNumber": "光圈值",
                    "ISOSpeedRatings": "ISO值",
                    "DateTimeOriginal": "原始时间",
                    "ExposureBiasValue": "曝光补偿",
                    "MeteringMode": "测光模式",
                    # "Flash": "闪光灯",
                    # 添加更多EXIF标签的中文翻译
                }
                # 增加测光模式的映射
                metering_mode_mapping = {
                    0: "未知",
                    1: "平均测光",
                    2: "中央重点测光",
                    3: "点测光",
                    4: "多点测光",
                    5: "多区域测光",
                    6: "部分测光",
                    255: "其他"
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
                        elif k == "MeteringMode":
                            # 将测光模式的数值转换为对应的中文描述
                            metering_mode = metering_mode_mapping.get(v, "其他")
                            exif_info_list.append(f"{k_cn}: {metering_mode}")
                        else:
                            exif_info_list.append(f"{k_cn}: {v}")
                exif_info = "\n".join(exif_info_list)
                exif_info =  exif_info + "\n" + exif_size_info
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
        max_scale = 100.0
        new_scale = current_scale * zoom_factor

        if min_scale <= new_scale <= max_scale:
            center = view.mapToScene(view.viewport().rect().center())
            view.scale(zoom_factor, zoom_factor)
            view.centerOn(center)

    def closeEvent(self, event):
        self.closed.emit()  # 发射关闭信号
        event.accept()
    def rotate_left(self):
        self.rotate_image(-90)

    def rotate_right(self):
        self.rotate_image(90)

    def rotate_image(self, angle):
        cursor_pos = QCursor.pos()
        pos = self.mapFromGlobal(cursor_pos)

        for view in self.graphics_views:
            local_pos = view.mapFromParent(pos)
            if view.rect().contains(local_pos):
                items = view.items(local_pos)
                if items:
                    pixmap_item = items[0]
                    # 获取当前缩放比例
                    current_scale = view.transform().m11()
                    # 旋转
                    pixmap_item.setRotation(pixmap_item.rotation() + angle)
                    # 保持缩放比例
                    pixmap_item.setScale(current_scale)
                break

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return  # 忽略自动重复事件

        if event.key() == Qt.Key_Q:
            self.handle_overlay('q')
        elif event.key() == Qt.Key_W:
            self.handle_overlay('w')
        else:
            super(SubMainWindow, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return  # 忽略自动重复事件

        if event.key() == Qt.Key_Q:
            self.restore_images('q')
        elif event.key() == Qt.Key_W:
            self.restore_images('w')
        else:
            super(SubMainWindow, self).keyReleaseEvent(event)

    def handle_overlay(self, key):
        print(f"handle_overlay called with key: {key}, number of images: {len(self.images)}")
        if len(self.images) != 2:
            QMessageBox.warning(self, "警告", "只有两张图片时才能使用覆盖比较功能。")
            return

        if key == 'q':
            # 将右侧图片覆盖到左侧
            right_pixmap = self.original_pixmaps[1]
            if right_pixmap:
                print("覆盖右侧图片到左侧")
                try:
                    self.graphics_views[0].pixmap_items[0].setPixmap(right_pixmap)
                except AttributeError as e:
                    print(f"Error during overlay with key 'q': {e}")
        elif key == 'w':
            # 将左侧图片覆盖到右侧
            left_pixmap = self.original_pixmaps[0]
            if left_pixmap:
                print("覆盖左侧图片到右侧")
                try:
                    self.graphics_views[1].pixmap_items[0].setPixmap(left_pixmap)
                except AttributeError as e:
                    print(f"Error during overlay with key 'w': {e}")

    def restore_images(self, key):
        if len(self.images) != 2:
            return  # 无需恢复

        if key == 'q':
            # 恢复左侧图片
            original_left_pixmap = self.original_pixmaps[0]
            if original_left_pixmap:
                if self.graphics_views[0].pixmap_items:
                    print("恢复左侧图片")
                    try:
                        self.graphics_views[0].pixmap_items[0].setPixmap(original_left_pixmap)
                    except AttributeError as e:
                        print(f"Error during restoring with key 'q': {e}")
                else:
                    print("Error: graphics_views[0].pixmap_items is empty")
        elif key == 'w':
            # 恢复右侧图片
            original_right_pixmap = self.original_pixmaps[1]
            if original_right_pixmap:
                if self.graphics_views[1].pixmap_items:
                    print("恢复右侧图片")
                    try:
                        self.graphics_views[1].pixmap_items[0].setPixmap(original_right_pixmap)
                    except AttributeError as e:
                        print(f"Error during restoring with key 'w': {e}")
                else:
                    print("Error: graphics_views[1].pixmap_items is empty")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubMainWindow(two_pic)
    window.show()
    sys.exit(app.exec_())
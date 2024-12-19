import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QFileDialog, QLabel, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
from PyQt5.QtCore import QSettings, Qt

class PreviewDialog(QDialog):
    def __init__(self, rename_data):
        super().__init__()
        self.setWindowTitle('重命名预览')
        self.resize(1200, 800)

        layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['文件夹', '旧文件名', '新文件名'])
        self.table.setRowCount(len(rename_data))

        for row, (folder, old_name, new_name) in enumerate(rename_data):
            self.table.setItem(row, 0, QTableWidgetItem(folder))
            self.table.setItem(row, 1, QTableWidgetItem(old_name))
            self.table.setItem(row, 2, QTableWidgetItem(new_name))

        # 设置表格列宽自适应
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.table)
        self.setLayout(layout)

class FileOrganizer(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings('MyApp', 'FileOrganizer')
        self.initUI()

    def initUI(self):
        # 设置窗口初始大小
        self.resize(1200, 800)

        # 主布局
        main_layout = QVBoxLayout()

        # 文件夹选择布局
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit(self)
        self.import_button = QPushButton('导入', self)
        self.import_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.import_button)

        # 文件夹和文件计数显示
        count_layout = QHBoxLayout()
        self.folder_count_label = QLabel('文件夹数量: 0', self)
        self.file_count_label = QLabel('文件总数: 0', self)
        count_layout.addWidget(self.folder_count_label)
        count_layout.addStretch()

        # 文件列表布局
        list_layout = QHBoxLayout()
        self.left_list = QTreeWidget(self)
        self.left_list.setHeaderHidden(True)

        # 右侧布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.file_count_label)  # 将文件总数标签放在右侧布局的顶部
        self.right_list = QTreeWidget(self)
        self.right_list.setHeaderHidden(True)
        right_layout.addWidget(self.right_list)

        # 右侧下方布局
        bottom_layout = QHBoxLayout()
        self.replace_checkbox = QCheckBox('查找替换', self)
        self.replace_checkbox.stateChanged.connect(self.toggle_replace)
        self.line_edit = QLineEdit(self)
        self.replace_line_edit = QLineEdit(self)
        self.replace_line_edit.setPlaceholderText('请输入替换内容')
        self.replace_line_edit.setVisible(False)  # 默认隐藏

        self.start_button = QPushButton('开始', self)
        self.start_button.clicked.connect(self.rename_files)
        self.preview_button = QPushButton('预览', self)
        self.preview_button.clicked.connect(self.preview_rename)
        bottom_layout.addWidget(self.replace_checkbox)
        bottom_layout.addWidget(self.line_edit)
        bottom_layout.addWidget(self.replace_line_edit)
        bottom_layout.addWidget(self.start_button)
        bottom_layout.addWidget(self.preview_button)
        right_layout.addLayout(bottom_layout)

        # 按钮布局
        button_layout = QVBoxLayout()
        self.add_button = QPushButton('增加', self)
        self.add_button.clicked.connect(self.add_to_right)
        self.add_all_button = QPushButton('增加全部', self)
        self.add_all_button.clicked.connect(self.add_all_to_right)
        self.remove_button = QPushButton('移除', self)
        self.remove_button.clicked.connect(self.remove_from_right)
        
        # 新增"移除全部"按钮
        self.remove_all_button = QPushButton('移除全部', self)
        self.remove_all_button.clicked.connect(self.remove_all_from_right)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.add_all_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.remove_all_button)  # 添加"移除全部"按钮

        # 将组件添加到列表布局
        list_layout.addWidget(self.left_list)
        list_layout.addLayout(button_layout)
        list_layout.addLayout(right_layout)

        # 布局设置
        main_layout.addLayout(folder_layout)
        main_layout.addLayout(count_layout)
        main_layout.addLayout(list_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('文件夹管理器')

        # 加载上次打开的文件夹
        last_folder = self.settings.value('lastFolder', '')
        if last_folder:
            self.folder_input.setText(last_folder)
            self.populate_left_list(last_folder)

        self.show()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder:
            self.folder_input.setText(folder)
            self.populate_left_list(folder)
            # 保存当前文件夹路径
            self.settings.setValue('lastFolder', folder)

    def populate_left_list(self, folder):
        self.left_list.clear()
        self.right_list.clear()
        folder_count = 0
        for subfolder in os.listdir(folder):
            subfolder_path = os.path.join(folder, subfolder)
            if os.path.isdir(subfolder_path):
                folder_item = QTreeWidgetItem(self.left_list, [subfolder])
                for file in os.listdir(subfolder_path):
                    file_path = os.path.join(subfolder_path, file)
                    if os.path.isfile(file_path):
                        QTreeWidgetItem(folder_item, [file])
                folder_count += 1
        self.folder_count_label.setText(f'文件夹数量: {folder_count}')
        self.update_file_count()

    def add_to_right(self):
        selected_items = self.left_list.selectedItems()
        for item in selected_items:
            folder_item = QTreeWidgetItem(self.right_list, [item.text(0)])
            for i in range(item.childCount()):
                QTreeWidgetItem(folder_item, [item.child(i).text(0)])
        self.update_file_count()

    def add_all_to_right(self):
        self.right_list.clear()
        for i in range(self.left_list.topLevelItemCount()):
            item = self.left_list.topLevelItem(i)
            folder_item = QTreeWidgetItem(self.right_list, [item.text(0)])
            for j in range(item.childCount()):
                QTreeWidgetItem(folder_item, [item.child(j).text(0)])
        self.update_file_count()

    def remove_from_right(self):
        selected_items = self.right_list.selectedItems()
        for item in selected_items:
            index = self.right_list.indexOfTopLevelItem(item)
            self.right_list.takeTopLevelItem(index)
        self.update_file_count()

    def remove_all_from_right(self):
        self.right_list.clear()
        self.update_file_count()

    def update_file_count(self):
        file_count = 0
        for i in range(self.right_list.topLevelItemCount()):
            item = self.right_list.topLevelItem(i)
            file_count += item.childCount()
        self.file_count_label.setText(f'文件总数: {file_count}')

    def toggle_replace(self, state):
        self.replace_line_edit.setVisible(state == Qt.Checked)

    def rename_files(self):
        prefix = self.line_edit.text()
        replace_text = self.replace_line_edit.text() if self.replace_checkbox.isChecked() else None
        hash_count = prefix.count('#')

        for i in range(self.right_list.topLevelItemCount()):
            folder_item = self.right_list.topLevelItem(i)
            folder_name = folder_item.text(0)
            folder_path = os.path.join(self.folder_input.text(), folder_name)

            for j in range(folder_item.childCount()):
                file_item = folder_item.child(j)
                original_name = file_item.text(0)
                original_path = os.path.join(folder_path, original_name)

                # 如果prefix为空，则保持原文件名
                if not prefix:
                    new_name = original_name
                else:
                    if hash_count > 0:
                        number_format = f'{{:0{hash_count}d}}'
                        new_name = prefix.replace('#' * hash_count, number_format.format(j))
                    else:
                        new_name = prefix

                    new_name = new_name.replace('$p', folder_name)
                    file_extension = os.path.splitext(original_name)[1]

                    if '*' in prefix:
                        new_name += original_name
                    else:
                        new_name += file_extension

                    new_name = new_name.replace('*', '')

                    if replace_text:
                        new_name = original_name.replace(prefix, replace_text)

                new_path = os.path.join(folder_path, new_name)

                print(f'Trying to rename: {original_path} to {new_path}')
                if not os.path.exists(original_path):
                    print(f'File does not exist: {original_path}')
                    continue

                try:
                    os.rename(original_path, new_path)
                    print(f'Renamed {original_name} to {new_name}')
                except Exception as e:
                    print(f'Error renaming {original_name}: {e}')

        self.refresh_file_lists()

    def refresh_file_lists(self):
        # 重新填充左侧列表
        current_folder = self.folder_input.text()
        if current_folder:
            self.populate_left_list(current_folder)

    def preview_rename(self):
        rename_data = []
        prefix = self.line_edit.text()
        replace_text = self.replace_line_edit.text() if self.replace_checkbox.isChecked() else None
        hash_count = prefix.count('#')

        for i in range(self.right_list.topLevelItemCount()):
            folder_item = self.right_list.topLevelItem(i)
            folder_name = folder_item.text(0)
            folder_path = os.path.join(self.folder_input.text(), folder_name)

            for j in range(folder_item.childCount()):
                file_item = folder_item.child(j)
                original_name = file_item.text(0)

                # 如果prefix为空，则保持原文件名
                if not prefix:
                    new_name = original_name
                else:
                    if hash_count > 0:
                        number_format = f'{{:0{hash_count}d}}'
                        new_name = prefix.replace('#' * hash_count, number_format.format(j))
                    else:
                        new_name = prefix

                    new_name = new_name.replace('$p', folder_name)
                    file_extension = os.path.splitext(original_name)[1]

                    if '*' in prefix:
                        new_name += original_name
                    else:
                        new_name += file_extension

                    new_name = new_name.replace('*', '')

                    if replace_text:
                        new_name = original_name.replace(prefix, replace_text)

                rename_data.append((folder_path, original_name, new_name))

        if rename_data:
            dialog = PreviewDialog(rename_data)
            dialog.exec_()
        else:
            print("没有可预览的重命名数据")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileOrganizer()
    sys.exit(app.exec_())
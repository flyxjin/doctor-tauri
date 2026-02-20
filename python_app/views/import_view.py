
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QProgressBar, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QCheckBox, QTabWidget,
                             QSplitter, QGroupBox, QTextEdit, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_importer import DataImporter


class ImportView(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        tab_widget = QTabWidget()
        
        import_tab = self.create_import_tab()
        history_tab = self.create_history_tab()
        
        tab_widget.addTab(import_tab, '数据导入')
        tab_widget.addTab(history_tab, '导入历史')
        
        main_layout.addWidget(tab_widget)
    
    def create_import_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        file_group = QGroupBox('选择文件')
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel('未选择文件')
        self.file_label.setStyleSheet('color: gray;')
        browse_btn = QPushButton('浏览...')
        browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(browse_btn)
        file_group.setLayout(file_layout)
        
        options_group = QGroupBox('导入选项')
        options_layout = QHBoxLayout()
        
        self.skip_existing_cb = QCheckBox('跳过已存在的药材')
        self.skip_existing_cb.setChecked(True)
        
        options_layout.addWidget(self.skip_existing_cb)
        options_layout.addStretch()
        options_group.setLayout(options_layout)
        
        progress_group = QGroupBox('导入进度')
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        self.status_label = QLabel('准备就绪')
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_group.setLayout(progress_layout)
        
        btn_layout = QHBoxLayout()
        
        self.import_btn = QPushButton('开始导入')
        self.import_btn.setStyleSheet('''
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 30px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        ''')
        self.import_btn.clicked.connect(self.start_import)
        
        template_btn = QPushButton('下载模板')
        template_btn.clicked.connect(self.download_template)
        
        btn_layout.addStretch()
        btn_layout.addWidget(template_btn)
        btn_layout.addWidget(self.import_btn)
        btn_layout.addStretch()
        
        log_group = QGroupBox('导入日志')
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 9))
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        layout.addWidget(file_group)
        layout.addWidget(options_group)
        layout.addWidget(progress_group)
        layout.addLayout(btn_layout)
        layout.addWidget(log_group, 1)
        
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_history)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(9)
        self.history_table.setHorizontalHeaderLabels([
            'ID', '任务名称', '类型', '总数', '已处理', 
            '成功', '失败', '状态', '创建时间'
        ])
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        top_layout.addWidget(refresh_btn)
        top_layout.addWidget(self.history_table)
        
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        bottom_layout.addWidget(QLabel('任务详情:'))
        
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels([
            '行号', '药材名称', '状态', '错误信息', '时间'
        ])
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        bottom_layout.addWidget(self.logs_table)
        
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        self.load_history()
        
        return widget
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择数据文件', '', 
            'CSV文件 (*.csv);;JSON文件 (*.json);;所有文件 (*.*)'
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(file_path)
            self.file_label.setStyleSheet('color: #2c3e50;')
    
    def download_template(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存模板文件', '中药数据模板.csv',
            'CSV文件 (*.csv)'
        )
        if file_path:
            try:
                importer = DataImporter(self.db)
                template = importer.get_template_csv()
                
                example_data = 'name,alias,category,nature,taste,meridian,efficacy,indications,usage,dosage,contraindication,notes,source,price,quantity,min_stock\n'
                example_data += '人参,黄参、地精,补虚药,温,甘、微苦,归脾、肺、心经,大补元气，复脉固脱,体虚欲脱，肢冷脉微,煎服,3-9g,实证忌服,,《中国药典》,50,100,10\n'
                example_data += '黄芪,棉芪,补虚药,微温,甘,归脾、肺经,补气升阳，固表止汗,气虚乏力，食少便溏,煎服,9-30g,表实邪盛忌服,,《中国药典》,20,200,10\n'
                
                with open(file_path, 'w', encoding='utf-8-sig') as f:
                    f.write(template)
                    f.write(example_data)
                
                QMessageBox.information(self, '成功', '模板下载成功！\n\n模板包含示例数据，您可以参考格式填写。')
            except Exception as e:
                QMessageBox.critical(self, '错误', '下载模板失败: ' + str(e))
    
    def start_import(self):
        if not hasattr(self, 'file_path'):
            QMessageBox.warning(self, '提示', '请先选择要导入的文件')
            return
        
        if not os.path.exists(self.file_path):
            QMessageBox.warning(self, '提示', '文件不存在')
            return
        
        task_name = os.path.basename(self.file_path)
        ext = os.path.splitext(self.file_path)[1].lower()
        
        if ext == '.csv':
            source_type = 'csv'
        elif ext == '.json':
            source_type = 'json'
        else:
            QMessageBox.warning(self, '提示', '不支持的文件格式，请选择CSV或JSON文件')
            return
        
        self.import_btn.setEnabled(False)
        self.log_text.clear()
        self.log_text.append('开始导入...\n')
        
        try:
            importer = DataImporter(self.db)
            
            def progress_callback(current, total, success, failed):
                self.progress_bar.setMaximum(total)
                self.progress_bar.setValue(current)
                self.status_label.setText('处理中: ' + str(current) + '/' + str(total) + ' | 成功: ' + str(success) + ' | 失败: ' + str(failed))
                
                if current % 50 == 0 or current == total:
                    self.log_text.append('已处理 ' + str(current) + '/' + str(total) + ' 条记录...')
            
            if source_type == 'csv':
                result = importer.import_from_csv(
                    self.file_path, task_name, progress_callback, 
                    self.skip_existing_cb.isChecked()
                )
            else:
                result = importer.import_from_json(
                    self.file_path, task_name, progress_callback, 
                    self.skip_existing_cb.isChecked()
                )
            
            self.import_btn.setEnabled(True)
            
            if result['success']:
                msg = '导入完成！\n\n总数: ' + str(result['total']) + '\n成功: ' + str(result['success_count']) + '\n失败: ' + str(result['failed_count'])
                QMessageBox.information(self, '完成', msg)
                self.log_text.append('\n导入成功完成！')
                self.status_label.setText('导入完成')
            else:
                QMessageBox.critical(self, '失败', '导入失败')
                
        except Exception as e:
            self.import_btn.setEnabled(True)
            QMessageBox.critical(self, '错误', '导入出错: ' + str(e))
            self.log_text.append('\n错误: ' + str(e))
            self.status_label.setText('导入失败')
    
    def load_history(self):
        tasks = self.db.get_import_tasks()
        self.history_table.setRowCount(len(tasks))
        
        for row_idx, task in enumerate(tasks):
            for col_idx, data in enumerate(task):
                item = QTableWidgetItem(str(data) if data is not None else '')
                self.history_table.setItem(row_idx, col_idx, item)
    
    def show_task_logs(self):
        pass


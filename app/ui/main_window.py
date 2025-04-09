from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QRadioButton, QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QComboBox
from PyQt6.QtCore import Qt
from app.database.database import DB


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор НДФЛ")
        self.setMinimumSize(200, 500)
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch(1)

        # Title
        self.title_label = QLabel("<h1>Калькулятор налоговой базы и НДФЛ</h1>")
        self.main_layout.addWidget(self.title_label)

        # Choose staff
        self.staff_layout = QHBoxLayout()
        self.main_layout.addLayout(self.staff_layout)
        self.staff_label = QLabel("Сотрудник:")
        self.staff_combobox = QComboBox()
        self.add_item_to_combobox()
        self.staff_combobox.currentIndexChanged.connect(self.on_staff_changed)
        self.staff_layout.addWidget(self.staff_label)
        self.staff_layout.addWidget(self.staff_combobox)

        # Benefits and result
        self.benefits_result_layout = QHBoxLayout()
        self.benefits_result_layout.setContentsMargins(0, 20, 0, 0)
        self.main_layout.addLayout(self.benefits_result_layout)
        # Benefits
        self.benefits_layout = QVBoxLayout()
        self.add_benefits()
        self.benefits_result_layout.addLayout(self.benefits_layout)
        # Result
        self.result_label = QLabel("Результат: ")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignBaseline)
        self.benefits_result_layout.addWidget(self.result_label)

        # Type operation
        self.type_operation_label = QLabel("Тип операции: ")
        self.main_layout.addWidget(self.type_operation_label)
        self.type_operation_radiobutton_layout = QHBoxLayout()
        self.ndfl_button = QRadioButton("НДФЛ")
        self.tax_base = QRadioButton("Налоговая база")
        self.type_operation_radiobutton_layout.addWidget(self.tax_base)
        self.type_operation_radiobutton_layout.addWidget(self.ndfl_button)
        self.main_layout.addLayout(self.type_operation_radiobutton_layout)


        # Calculate button
        self.calculate_layout = QHBoxLayout()
        self.main_layout.addStretch(1)
        self.call_button = QPushButton("Рассчитать")
        self.call_button.clicked.connect(self.calculate_result)
        self.record_button = QPushButton("Записать")
        self.record_button.clicked.connect(self.record_result)
        self.calculate_layout.addWidget(self.call_button)
        self.calculate_layout.addSpacing(100)
        self.calculate_layout.addWidget(self.record_button)
        self.main_layout.addLayout(self.calculate_layout)
        self.main_layout.addStretch(1)

    def add_item_to_combobox(self):
        staff = DB.get_staff()
        for staffer in staff:
            self.staff_combobox.addItem(f"{staffer[1]} {staffer[2]}", userData=staffer[0])

    def on_staff_changed(self, index):
        try:
            staff_id = self.staff_combobox.itemData(index)
            self.staffer_info = DB.get_staffer_benefits(staff_id)
            self.veteran_checkbox.setChecked(self.staffer_info[0][0])
            self.children_checkbox.setChecked(self.staffer_info[0][1])
        except Exception as e:
            print(e)

    def add_benefits(self):
        self.veteran_checkbox = QCheckBox("Ветеран")
        self.veteran_checkbox.setObjectName("1")
        self.benefits_layout.addWidget(self.veteran_checkbox)
        self.children_checkbox = QCheckBox("Дети")
        self.children_checkbox.setObjectName("2")
        self.benefits_layout.addWidget(self.children_checkbox)

    def calculate_result(self):
        staff_id = self.staff_combobox.itemData(self.staff_combobox.currentIndex())
        res = DB.calculate_result(
            staff_id,
            self.tax_base.isChecked(),
            self.ndfl_button.isChecked(),
            self.veteran_checkbox.isChecked(),
            self.children_checkbox.isChecked()
        )
        self.result_label.setText(f"Результат: {res[0]}")

    def record_result(self):
        try:
            staff_id = self.staff_combobox.itemData(self.staff_combobox.currentIndex())
            res = DB.record_result(
                staff_id,
                self.tax_base.isChecked(),
                self.ndfl_button.isChecked(),
                self.veteran_checkbox.isChecked(),
                self.children_checkbox.isChecked()
            )
            self.result_label.setText(f"Результат: {res}")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from qt_material import apply_stylesheet

    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_pink.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QRadioButton, QCheckBox, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QComboBox, QFrame, QGridLayout
from PyQt6.QtCore import Qt
import re

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
        self.staff_frame = QFrame()
        self.staff_layout = QHBoxLayout()
        self.staff_frame.setLayout(self.staff_layout)
        self.main_layout.addWidget(self.staff_frame)
        self.staff_label = QLabel("Сотрудник:")
        self.staff_combobox = QComboBox()
        self.staff_combobox.setStyleSheet(
            """color: #fff"""
        )
        self.add_item_to_combobox()
        self.staff_combobox.currentIndexChanged.connect(self.on_staff_changed)
        self.staff_layout.addWidget(self.staff_label)
        self.staff_layout.addWidget(self.staff_combobox)

        # Benefits and result
        self.benefits_result_layout = QHBoxLayout()
        self.benefits_result_layout.setContentsMargins(0, 20, 0, 0)
        self.main_layout.addLayout(self.benefits_result_layout)
        # Benefits
        self.benefits_frame = QFrame()
        self.benefits_layout = QVBoxLayout()
        self.benefits_frame.setLayout(self.benefits_layout)
        self.add_benefits()
        self.benefits_result_layout.addWidget(self.benefits_frame)
        # Result
        self.result_frame = QFrame()
        self.result_layout = QHBoxLayout()
        self.result_frame.setLayout(self.result_layout)
        self.result_label = QLabel("Результат: ")
        self.result_layout.addWidget(self.result_label)
        self.benefits_result_layout.addWidget(self.result_frame)

        # Type operation
        self.type_operation_frame = QFrame()
        self.type_operation_layout = QVBoxLayout()
        self.type_operation_frame.setLayout(self.type_operation_layout)
        self.type_operation_label = QLabel("Тип операции: ")
        self.type_operation_layout.addWidget(self.type_operation_label)
        self.type_operation_radiobutton_layout = QGridLayout()
        self.add_operations()
        self.type_operation_layout.addLayout(self.type_operation_radiobutton_layout)
        self.main_layout.addSpacing(20)
        self.main_layout.addWidget(self.type_operation_frame)


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
            self.checkboxs[0].setChecked(self.staffer_info[0][0])
            self.checkboxs[1].setChecked(self.staffer_info[0][1])
        except Exception as e:
            print(e)

    def add_benefits(self):
        benefits = DB.get_type_benefits()
        self.checkboxs = []

        for index, benefit in enumerate(benefits):
            checkbox = QCheckBox(benefit[1])
            checkbox.setObjectName(str(benefit[0]))

            # Только первые два активны, остальные отключаются
            if index >= 2:
                checkbox.setDisabled(True)

            self.checkboxs.append(checkbox)
            self.benefits_layout.addWidget(checkbox)
        # self.veteran_checkbox = QCheckBox("Ветеран")
        # self.veteran_checkbox.setObjectName("1")
        # self.benefits_layout.addWidget(self.veteran_checkbox)
        # self.children_checkbox = QCheckBox("Дети")
        # self.children_checkbox.setObjectName("2")
        # self.benefits_layout.addWidget(self.children_checkbox)

    import re

    def safe_attr_name(self, name):
        # Преобразуем в безопасное имя на латинице
        return re.sub(r'\W|^(?=\d)', '_', name)

    def add_operations(self):
        operations = DB.get_type_operation()
        self.operation_buttons = []  # список всех радиокнопок

        for index, operation in enumerate(operations):
            op_name = operation[1]  # Например, 'Налоговая база'

            radio_button = QRadioButton(op_name)

            # Только первые две активны
            if index >= 2:
                radio_button.setDisabled(True)

            # Сохраняем в список
            self.operation_buttons.append(radio_button)

            # Создаём безопасное имя атрибута
            attr_name = f"{self.safe_attr_name(op_name)}_button"
            setattr(self, attr_name, radio_button)

            # Раскладка по строкам и столбцам
            row = index // 2
            col = index % 2
            self.type_operation_radiobutton_layout.addWidget(radio_button, row, col)

    def calculate_result(self):
        staff_id = self.staff_combobox.itemData(self.staff_combobox.currentIndex())
        res = DB.calculate_result(
            staff_id,
            self.Налоговая_база_button.isChecked(),
            self.НДФЛ_button.isChecked(),
            self.checkboxs[0].isChecked(),
            self.checkboxs[1].isChecked()
        )
        res = res[0] if res[0] else "Ошибка"
        self.result_label.setText(f"Результат: {res}")

    def record_result(self):
        try:
            staff_id = self.staff_combobox.itemData(self.staff_combobox.currentIndex())
            res = DB.record_result(
                staff_id,
                self.Налоговая_база_button.isChecked(),
                self.НДФЛ_button.isChecked(),
                self.checkboxs[0].isChecked(),
                self.checkboxs[1].isChecked()
            )
            res = res if res else "Ошибка"
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

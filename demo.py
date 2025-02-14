import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QLabel, QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt5 import QtWidgets

class InformationSystem(QMainWindow):
    def __init__(self):
        super(InformationSystem, self).__init__()
        self.setWindowTitle("Student Information System")
        self.resize(1260, 720)
        self.initUI()

    
    def initUI(self):

        # Main layout
        main_layout = QVBoxLayout()
        #secondary_layout = QVBoxLayout()

        # Buttons for opening CSV files
        self.open_button = QPushButton("Load Student CSV Files")
        self.open_button.setMinimumSize(200,50)
        self.open_button.setMaximumSize(200,50)
        self.open_button.move(50,50)
        self.open_button.clicked.connect(self.open_csv_file)
        
        # Button for adding student entry
        self.add_button = QPushButton("Add")
        self.add_button.setMinimumSize(100,50)
        self.add_button.setMaximumSize(100,50)
        self.add_button.move(50,50)
        self.add_button.clicked.connect(self.add_entry_window)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.add_button)        

        # Tab widget for displaying CSVs
        self.tab_widget = QTabWidget()

        # Add widgets to main layout
        main_layout.addLayout(button_layout)
        main_layout.addLayout(button_layout) #Add button       
        main_layout.addWidget(self.tab_widget)
       

        # Set central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # Add button functions
    def add_entry_window(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Add Student Entry')
        dialog.resize(800,600)
        
        layout = QFormLayout()
        idEdit = QLineEdit()
        firstNameEdit = QLineEdit()
        lastNameEdit = QLineEdit()
        yearEdit = QLineEdit()
        genderEdit = QLineEdit()

        layout.addRow('ID Number:', idEdit)
        layout.addRow('First Name:', firstNameEdit)
        layout.addRow('Last Name:', lastNameEdit)
        layout.addRow('Year Level:', yearEdit)
        layout.addRow('Gender:', genderEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        #buttonBox.accepted.connect(lambda: self.addEntry(nameEdit.text(), ageEdit.text(), gradeEdit.text(), dialog))
        #buttonBox.rejected.connect(dialog.reject)

        layout.addRow(buttonBox)
        dialog.setLayout(layout)
        dialog.exec_()

    def open_csv_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Student CSV Files", "", "CSV Files (*.csv);;All Files (*)", options=options)

        if file_path:
            self.add_csv_tab(file_path)

    def add_csv_tab(self, file_path):
        try:
            with open(file_path, "r", newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader, None)  # Get headers
                rows = list(reader)

            # Create a new tab with a table widget
            table_widget = QTableWidget()
            if headers:
                table_widget.setColumnCount(len(headers))
                table_widget.setHorizontalHeaderLabels(headers)

            table_widget.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, cell_data in enumerate(row_data):
                    table_widget.setItem(row_idx, col_idx, QTableWidgetItem(cell_data))

            table_name = file_path.split("/")[-1]
            self.tab_widget.addTab(table_widget, table_name)

        except Exception as e:
            error_label = QLabel(f"Failed to load CSV file: {str(e)}")
            error_tab = QWidget()
            error_layout = QVBoxLayout()
            error_layout.addWidget(error_label)
            error_tab.setLayout(error_layout)
            self.tab_widget.addTab(error_tab, "Error")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = InformationSystem()
    viewer.show()
    sys.exit(app.exec_())

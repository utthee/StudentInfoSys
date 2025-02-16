import sys
import csv
import re
import os

from collections import defaultdict
from main_UI import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5 import *

STUDENT_CSV = "STUDENT.csv"
PROGRAM_CSV = "PROGRAM.csv"
COLLEGE_CSV = "COLLEGE.csv"

class MainClass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.file_paths = [STUDENT_CSV,PROGRAM_CSV,COLLEGE_CSV]
        self.headers = [[], [], []]  # Store CSV headers
        self.current_table_index = self.displayComboBox.currentIndex()  # Track the current table being displayed
        self.data = [[], [], []]  # Store CSV data for each table
        self.open_csv_file()
        
        self.addStudentButton.clicked.connect(self.addStudentEntry)
        self.addProgramButton.clicked.connect(self.addProgramEntry)
        self.programChoices()
        self.addCollegeButton.clicked.connect(self.addCollegeEntry)
        self.collegeChoices()       

        self.pushButton.clicked.connect(self.deleteEntry)

        #self.sortComboBox.currentIndexChanged.connect(self.sortLayout)
        self.searchButton.clicked.connect(self.searchEntry)
        self.displayComboBox.currentIndexChanged.connect(self.switch_table)

    def open_csv_file(self):

        for i, file_path in enumerate(self.file_paths):
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    self.headers[i] = next(reader)
                    self.data[i] = [row for row in reader]
            except FileNotFoundError:
                print(f"Error: {file_path} not found.")
        
        self.display_table(self.current_table_index)

    def display_table(self, table_index):
        self.current_table_index = table_index
        self.tableWidget.setColumnCount(len(self.headers[table_index]))
        self.tableWidget.setHorizontalHeaderLabels(self.headers[table_index])
        self.tableWidget.setRowCount(len(self.data[table_index]))
        
        for row_idx, row in enumerate(self.data[table_index]):
            for col_idx, value in enumerate(row):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        
        self.sortComboBox.clear()
        self.sortComboBox.addItems(self.headers[self.current_table_index])

    def switch_table(self):
        new_index = self.displayComboBox.currentIndex()
        self.display_table(new_index)

        #self.sortComboBox.clear()
        #self.sortComboBox.addItems(self.headers)
    
    def addStudentEntry(self):
        idNumber = self.idNumberEdit.text()
        firstName = self.firstNameEdit.text()
        lastName = self.lastNameEdit.text()
        yearLevel = self.yearLevelComboBox.currentText()
        gender = self.genderComboBox.currentText()
        programCode = self.programCodeBox.currentText()

        if self.current_table_index != 0:
            QMessageBox.warning(self, "Incorrect displayed table", "Must be on student table to add.")
            return

        if not re.fullmatch(r'20\d{2}-\d{4}', idNumber):
            QMessageBox.warning(self, "Invalid ID Format", "ID Number must be in the format 20XX-XXXX where X is a digit.")
            return
        
        if idNumber and firstName and lastName and yearLevel and gender and programCode:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            self.tableWidget.setItem(row_position, 0, QTableWidgetItem(idNumber))
            self.tableWidget.setItem(row_position, 1, QTableWidgetItem(firstName))
            self.tableWidget.setItem(row_position, 2, QTableWidgetItem(lastName))
            self.tableWidget.setItem(row_position, 3, QTableWidgetItem(yearLevel))
            self.tableWidget.setItem(row_position, 4, QTableWidgetItem(gender))
            self.tableWidget.setItem(row_position, 5, QTableWidgetItem(programCode))
        
        if self.file_paths[0]:
            with open(self.file_paths[0], 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([idNumber, firstName, lastName, yearLevel, gender, programCode])
        
            self.idNumberEdit.clear()
            self.firstNameEdit.clear()
            self.lastNameEdit.clear()

    def programChoices(self):
        with open(self.file_paths[1], "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.programCodeBox.clear()
            self.programCodeBox.addItem("")
            self.programCodeBox.addItems(program_codes)

    def deleteEntry(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            if self.displayComboBox.currentIndex() == 0:
                stdMsg = QMessageBox(self)
                stdMsg.setWindowTitle("Delete Student")
                stdMsg.setText("Are you sure you want to delete this student entry?")
                stdMsg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                result = stdMsg.exec_()
                if result == QMessageBox.Yes:
                    self.deleteProcess(selected_row)
                else:
                    return
                
            elif self.displayComboBox.currentIndex() == 1:
                prgMsg = QMessageBox(self)
                prgMsg.setWindowTitle("Delete Program")
                prgMsg.setText("Are you sure you want to delete this program. All students under this program will be unenrolled.")
                prgMsg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                result = prgMsg.exec_()
                if result == QMessageBox.Yes:
                    self.deleteProcess(selected_row)
                else:
                    return
                
            elif self.displayComboBox.currentIndex() == 2:
                clgMsg = QMessageBox(self)
                prgMsg.setWindowTitle("Delete College")
                prgMsg.setText("Are you sure you want to delete this College. All programs under this college will also be deleted.")
                clgMsg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                result = clgMsg.exec_()
                if result == QMessageBox.Yes:
                    self.deleteProcess(selected_row)
                else:
                    return
                
        else:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")

    def deleteProcess(self, selected_row):        
            self.tableWidget.removeRow(selected_row)
            if self.file_paths[self.displayComboBox.currentIndex()]:
                data = []
                with open(self.file_paths[self.displayComboBox.currentIndex()], newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    headers = next(reader)  # Keep headers
                    data = [row for row in reader]
                
                # Remove selected row from data list
                if 0 <= selected_row < len(data):
                    del data[selected_row]
                
                # Rewrite CSV file
                with open(self.file_paths[self.displayComboBox.currentIndex()], 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)  # Write headers back
                    writer.writerows(data)            
    
    def updateStudentEntry(self):
        pass

    """
    def sortLayout(self, i):
        selected_header = self.sortComboBox.currentText()
        if selected_header and selected_header in self.headers:
            col_index = self.headers.index(selected_header)
            self.headers.insert(0, self.headers.pop(col_index))
            
            data = []
            for row in range(self.tableWidget.rowCount()):
                data.append([self.tableWidget.item(row, col).text() if self.tableWidget.item(row, col) else "" for col in range(self.tableWidget.columnCount())])
            
            for row in data:
                row.insert(0, row.pop(col_index))
            
            self.tableWidget.setHorizontalHeaderLabels(self.headers)
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(value))
    """

    def addProgramEntry(self):
        programCode = self.programCodeEdit2.text().strip().upper()
        programName = self.programNameEdit.text()
        collegeCode = self.collegeCodeBox.currentText()

        if self.current_table_index != 1:
            QMessageBox.warning(self, "Incorrect displayed table", "Must be on program table to add.")
            return
        
        if not programCode or not programName or not collegeCode:
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return
        
        if not programCode.isalpha() or not programName.isalpha() or not collegeCode.isalpha():
            QMessageBox.warning(self, "Input Error", "Must not contain a digit.")
            return

        new_row = [programCode, programName, collegeCode]
        self.data[1].append(new_row)

        # Write everything back to the file
        with open(self.file_paths[1], 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.data[1])  # Writes each row separately
        
        self.open_csv_file()

        self.collegeCodeEdit2.clear()
        self.collegeNameEdit.clear()

    def addCollegeEntry(self):
        collegeCode = self.collegeCodeEdit2.text().strip().upper()
        collegeName = self.collegeNameEdit.text()

        #CHECK WHETHER THE DISPLAYED TABLE IS THE CORRECT ONE
        if self.current_table_index != 2:
            QMessageBox.warning(self, "Incorrect displayed table", "Must be on college table to add.")
            return

        if not collegeCode or not collegeName:
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return

        # Append the new row properly
        new_row = [collegeCode, collegeName]
        self.data[2].append(new_row)

        # Write everything back to the file
        with open(self.file_paths[2], 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.data[2])  # Writes each row separately
        
        self.open_csv_file()

        self.collegeCodeEdit2.clear()
        self.collegeNameEdit.clear()

    def collegeChoices(self):
        with open(self.file_paths[2], "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.collegeCodeBox.clear()
            self.collegeCodeBox.addItem("")
            self.collegeCodeBox.addItems(college_codes)

    def searchEntry(self):
        searched_item = self.searchBox.text().lower()
        for row in range(self.tableWidget.rowCount()):
            match = any(searched_item in (self.tableWidget.item(row, col).text().lower() if self.tableWidget.item(row, col) else "") for col in range(self.tableWidget.columnCount()))
            self.tableWidget.setRowHidden(row, not match)
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainClass()
    main.show()
    app.exec_()
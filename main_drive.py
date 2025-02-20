import sys
import csv
import re
import os

from collections import defaultdict
from mainUI import Ui_MainWindow
from update import Ui_Dialog
from PyQt5.QtWidgets import *
from PyQt5 import *

STUDENT_CSV = "STUDENT.csv"
PROGRAM_CSV = "PROGRAM.csv"
COLLEGE_CSV = "COLLEGE.csv"

class MainClass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.file_paths = [STUDENT_CSV, PROGRAM_CSV, COLLEGE_CSV]
        self.headers = [[], [], []]  # Store CSV headers
        self.current_table_index = self.displayComboBox.currentIndex()  # Track the current table being displayed
        self.data = [[], [], []]  # Store CSV data for each table
        self.open_csv_file()
        
        self.addStudentButton.clicked.connect(self.addStudentEntry)
        self.addProgramButton.clicked.connect(self.addProgramEntry)
        self.addCollegeButton.clicked.connect(self.addCollegeEntry)       

        self.pushButton.clicked.connect(self.deleteEntry)
        self.pushButton_2.clicked.connect(self.updateEntry)

        self.sortComboBox.currentIndexChanged.connect(self.sortLayout)
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
            
        self.programChoices()
        self.collegeChoices()
        
        self.display_table(self.displayComboBox.currentIndex())

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

        self.searchComboBox.clear()
        self.searchComboBox.addItems(self.headers[self.current_table_index])

    def switch_table(self):
        new_index = self.displayComboBox.currentIndex()
        self.display_table(new_index)

        #self.sortComboBox.clear()
        #self.sortComboBox.addItems(self.headers)
    
    def searchEntry(self):
        searched_item = self.searchBox.text().lower()
        search_filter = self.searchComboBox.currentText()

        header_labels = self.headers[self.current_table_index]
        filter_col_index = header_labels.index(search_filter)  # Get column index

        # Iterate through table rows and hide/show based on search match
        for row in range(self.tableWidget.rowCount()):
            cell_item = self.tableWidget.item(row, filter_col_index)
            cell_text = cell_item.text().lower() if cell_item else ""
            self.tableWidget.setRowHidden(row, searched_item not in cell_text)

        """
        for row in range(self.tableWidget.rowCount()):
            match = any(searched_item in (self.tableWidget.item(row, col).text().lower() if self.tableWidget.item(row, col) else "") for col in range(self.tableWidget.columnCount()))
            self.tableWidget.setRowHidden(row, not match)
        """

    def deleteEntry(self):
        if self.displayComboBox.currentIndex() == 0:
            self.deleteStudentEntry()
            return
        
        elif self.displayComboBox.currentIndex() == 1:
            self.deleteProgramEntry()
            return
        
        elif self.displayComboBox.currentIndex() == 2:
            self.deleteCollegeEntry()
            return
        
    def updateEntry(self):
        if self.current_table_index == 0:
            self.updateStudentEntry()
            return
        elif self.current_table_index == 1:
            self.updateProgramEntry()
            return
        elif self.current_table_index ==2:
            self.updateCollegeEntry()
            return
        
    def updateStudentEntry(self):
        self.readStudentCSV()
        selected_row = self.tableWidget.currentRow()
        
        data = self.data[0]
                
        if 0 <= selected_row < len(data):
            updateIDNumber = self.tableWidget.item(selected_row, 0).text()
            updateFirstName = self.tableWidget.item(selected_row, 1).text()
            updateLastName = self.tableWidget.item(selected_row, 2).text()
            updateYearLevel = self.tableWidget.item(selected_row, 3).text()
            updateGender = self.tableWidget.item(selected_row, 4).text()
            updateProgramCode = self.tableWidget.item(selected_row, 5).text()

            editor = Dialog(updateIDNumber, updateFirstName, updateLastName, updateYearLevel, updateGender, updateProgramCode)
            if editor.exec_():  # If the user clicks OK
                updated_values = editor.updatedStudentData()
                if 0 <= selected_row < len(data):
                    del data[selected_row]
                
                self.data[0].append(updated_values)
                self.updateStudentCSV(self.data[0])
                self.open_csv_file()

        self.updateStudentCSV(data)
        self.open_csv_file()

##################################################################################  STUDENT   #############################################################################################

    def addStudentEntry(self):
        self.readStudentCSV()
        
        idNumber = self.idNumberEdit.text()
        firstName = self.firstNameEdit.text().strip()
        lastName = self.lastNameEdit.text().strip()
        yearLevel = self.yearLevelComboBox.currentText()
        gender = self.genderComboBox.currentText()
        programCode = self.programCodeBox.currentText()

        if self.current_table_index != 0:
            QMessageBox.warning(self, "Table Mismatch", "Must be on student table to add.")
            return

        if not (idNumber and firstName and lastName and programCode):
            QMessageBox.warning(self, "Input Error", "All required fields must be field up.")
            return

        if not re.fullmatch(r'20\d{2}-\d{4}', idNumber):
            QMessageBox.warning(self, "Input Error", "Input a valid ID Number.")
            return
        
        if any(student[0] == idNumber for student in self.data[0]):  
            QMessageBox.warning(self, "Input Error", "The ID Number you're trying to enter already exists.")
            return
        
        if not all(char.isalpha() or char.isspace() for char in firstName and lastName):
            QMessageBox.warning(self, "Input Error", "Input a valid name.")
            return
        
        if idNumber and firstName and lastName and yearLevel and gender and programCode:
            studentData = [idNumber, firstName, lastName, yearLevel, gender, programCode]
            #self.readStudentCSV()
            self.data[0].append(studentData)

            self.updateStudentCSV(self.data[0])
            self.clearStudentInput()
            self.open_csv_file()

    def clearStudentInput(self):
        self.idNumberEdit.clear()
        self.firstNameEdit.clear()
        self.lastNameEdit.clear()
        self.yearLevelComboBox.setCurrentIndex(0)
        self.yearLevelComboBox.setCurrentIndex(0)
        self.programCodeBox.setCurrentIndex(0)

    def readStudentCSV(self):
        with open(STUDENT_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[0] = next(reader)  # Keep headers
            data = [row for row in reader]
            self.data[0] = data
    
    def updateStudentCSV(self, data):
            with open(STUDENT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.headers[0])  # Write headers back
                writer.writerows(data)
    
    def deleteStudentEntry(self):
        selected_row = self.tableWidget.currentRow()
        self.readStudentCSV()
        
        data = self.data[0]
                
        # Remove selected row from data list
        if 0 <= selected_row < len(data):
            del data[selected_row]

        self.updateStudentCSV(data)
        self.open_csv_file()


    """
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
                clgMsg.setWindowTitle("Delete College")
                clgMsg.setText("Are you sure you want to delete this College. All programs under this college will also be deleted.")
                clgMsg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                result = clgMsg.exec_()
                if result == QMessageBox.Yes:
                    self.deleteProcess(selected_row)
                    self.deletePrograms(selected_row)
                else:
                    return
                
        else:
            QMessageBox.warning(self, "No Selection", "Please select a row to delete.")
        
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
    

################################################################################################    PROGRAM     ###############################################################################

    def addProgramEntry(self):
        self.readProgramCSV()
        
        programCode = self.programCodeEdit2.text().strip().replace(" ","").upper()
        programName = self.programNameEdit.text().strip()
        collegeCode = self.collegeCodeBox.currentText()

        if self.current_table_index != 1:
            QMessageBox.warning(self, "Table Mismatch", "Must be on program table to add.")
            return
        
        if not (programCode and programName and collegeCode):
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return
        
        if not all(char.isalpha() or char.isspace() for char in programCode and programName):
            QMessageBox.warning(self, "Input Error", "Please input a valid program name.")
            return
        
        # Checks whether there are already existing inputs or not.
        if any(program[0] == programCode for program in self.data[1]):
            QMessageBox.warning(self, "Input Error", "The program you are trying to add already exists.")
            return
        
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)

            programDupe = programName.strip().replace(" ","").upper()

            for row in reader:
                if row[1].strip().replace(" ","").upper() == programDupe:
                    QMessageBox.warning(self, "Input Error", "The program you are trying to enter already exists.")
                    return

        if programCode and programName and collegeCode:
            program_data = [programCode, programName, collegeCode]
            self.data[1].append(program_data)

            self.updateProgramCSV(self.data[1])
            self.clearProgramInput()
            self.open_csv_file()
    
    def clearProgramInput(self):
        self.programCodeEdit2.clear()
        self.programNameEdit.clear()
        self.collegeCodeBox.setCurrentIndex(0)

    def readProgramCSV(self):
        with open(PROGRAM_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[1] = next(reader)  # Keep headers
            data = [row for row in reader]
            self.data[1] = data

    def updateProgramCSV(self, data):
        with open(PROGRAM_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[1])
            writer.writerows(data)  # Writes each row separately
    
    def deleteProgramEntry(self):
        selected_row = self.tableWidget.currentRow()

        program_code = self.tableWidget.item(selected_row, 0).text()

        #Remove from program data
        self.data[1] = [row for row in self.data[1] if row[0] != program_code]

        for row in self.data[0]:
            if row[5] == program_code:
                row[5] = "UNENROLLED"
            
        self.updateProgramCSV(self.data[1])
        self.updateStudentCSV(self.data[0])
        self.open_csv_file()

    def programChoices(self):
        with open(self.file_paths[1], "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.programCodeBox.clear()
            self.programCodeBox.addItem("")
            self.programCodeBox.addItems(program_codes)

########################################################################################  COLLEGE  ##############################################################################

    def addCollegeEntry(self):
        self.readCollegeCSV()
        collegeCode = self.collegeCodeEdit2.text().strip().replace(" ","").upper()
        collegeName = self.collegeNameEdit.text().strip().title()

        #CHECK WHETHER THE DISPLAYED TABLE IS THE CORRECT ONE
        if self.current_table_index != 2:
            QMessageBox.warning(self, "Incorrect displayed table", "Must be on college table to add.")
            return

        if not collegeCode or not collegeName:
            QMessageBox.warning(self, "Input Error", "All fields must be filled up.")
            return
        
        if not all(char.isalpha() or char.isspace() for char in collegeCode and collegeName):
            QMessageBox.warning(self, "Input Error", "Please input a valid college name.")
            return
        
        if any(college[1] == collegeCode for college in self.data[1]):
            QMessageBox.warning(self, "Input Error", "The college you are trying to enter already exists.")
            return

        with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)

            collegeDupe = collegeName.strip().replace(" ","").upper()

            for row in reader:
                if row[1].strip().replace(" ","").upper() == collegeDupe:
                    QMessageBox.warning(self, "Input Error", "The college you are trying to enter already exists.")
                    return

        if collegeCode and collegeName:
            college_data = [collegeCode, collegeName]
            self.data[2].append(college_data)

            self.updateCollegeCSV(self.data[2])
            self.clearCollegeInput()
            self.open_csv_file()
    
    def clearCollegeInput(self):
        self.collegeCodeEdit2.clear()
        self.collegeNameEdit.clear()
    
    def readCollegeCSV(self):
        with open(COLLEGE_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            self.headers[2] = next(reader)  # Keep headers
            data = [row for row in reader]
            self.data[2] = data

    def updateCollegeCSV(self, data):
        with open(COLLEGE_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers[2])
            writer.writerows(data)  # Writes each row separately
    
    def deleteCollegeEntry(self):
        selected_row = self.tableWidget.currentRow()
        #data = []

        college_code = self.tableWidget.item(selected_row, 0).text()
        
        # Remove from college_data
        self.data[2] = [row for row in self.data[2] if row[0] != college_code]
        
        # Find programs linked to the deleted college
        program_codes_to_remove = {row[0] for row in self.data[1] if row[2] == college_code}
        
        # Remove related programs
        self.data[1] = [row for row in self.data[1] if row[0] not in program_codes_to_remove]
        
        # Update related students to have 'UNENROLLED' as program code
        for row in self.data[0]:
            if row[5] in program_codes_to_remove:
                row[5] = "UNENROLLED"
        
        # Update tables
        self.updateCollegeCSV(self.data[2])
        self.updateProgramCSV(self.data[1])
        self.updateStudentCSV(self.data[0])
        self.open_csv_file()

    def collegeChoices(self):
        with open(self.file_paths[2], "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.collegeCodeBox.clear()
            self.collegeCodeBox.addItem("")
            self.collegeCodeBox.addItems(college_codes)

#----------------------------------------------------------------------- EDIT PROGRAM ----------------------------------------------------------------------

#----------------------------------------------------------------------- EDIT PROGRAM ------------------------------------------------------------------

class Dialog(QDialog, Ui_Dialog):
    def __init__(self, idNumber, firstName, lastName, yearLevel, gender, programCode):
        super().__init__()
        self.setupUi(self)

        self.programChoices()

        self.updateIDNumber.setText(idNumber)
        self.updateIDNumber.setReadOnly(True)

        self.updateFirstName.setText(firstName)
        self.updateFirstName.setReadOnly(True)

        self.updateLastName.setText(lastName)
        self.updateLastName.setReadOnly(True)

        self.updateYearLevelComboBox.setCurrentText(yearLevel)

        self.updateGenderComboBox.setCurrentText(gender)
        self.updateGenderComboBox.setEditable(False)

        self.updateProgramCodeComboBox.setCurrentText(programCode)

        self.pushButton.clicked.connect(self.accept)       
        self.pushButton_2.clicked.connect(self.reject)

    def programChoices(self):
        with open(PROGRAM_CSV, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.updateProgramCodeComboBox.clear()
            self.updateProgramCodeComboBox.addItems(program_codes)

    def updatedStudentData(self):
        
        if not self.updateProgramCodeComboBox:
            QMessageBox.warning(self, "Input Error", "All required fields must be field up.")
            return
        
        return [
            self.updateIDNumber.text(),
            self.updateFirstName.text(),
            self.updateLastName.text(),
            self.updateYearLevelComboBox.currentText(),
            self.updateGenderComboBox.currentText(),
            self.updateProgramCodeComboBox.currentText(),
        ]
            


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainClass()
    main.show()
    app.exec_()
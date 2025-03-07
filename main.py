from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QWidget, QLabel,QDateEdit,QLineEdit,QVBoxLayout,QHBoxLayout,QPushButton,QTableWidget,QTableWidgetItem, QHeaderView, QMessageBox, QCheckBox
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from sys import exit
# 

class FitnessApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FitTrack")
        self.resize(800,600)
        
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.kal_box = QLineEdit()
        self.kal_box.setPlaceholderText("Number of Calories")
        self.dist_box = QLineEdit()
        self.dist_box.setPlaceholderText("Distance")
        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter a description")
        self.submit_btn = QPushButton("Submit")
        self.add_btn = QPushButton("Add")
        self.del_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear")
        self.dark_mode = QCheckBox("Dark Mode")
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Id","Date","Calories","Distance","Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        
        # 

        self.master_layout = QHBoxLayout()
        
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()
     
        self.sub_row1 = QHBoxLayout()
        self.sub_row2 = QHBoxLayout()
        self.sub_row3 = QHBoxLayout()
        self.sub_row4 = QHBoxLayout()


        
        self.sub_row1.addWidget(QLabel("Date:"))
        self.sub_row1.addWidget(self.date_box)
        self.sub_row2.addWidget(QLabel("Cal: "))
        self.sub_row2.addWidget(self.kal_box)
        self.sub_row3.addWidget(QLabel("KM:"))
        self.sub_row3.addWidget(self.dist_box)
        self.sub_row4.addWidget(QLabel("Des:"))
        self.sub_row4.addWidget(self.description)
        
        
        self.col1.addLayout(self.sub_row1)
        self.col1.addLayout(self.sub_row2)
        self.col1.addLayout(self.sub_row3)
        self.col1.addLayout(self.sub_row4)
        self.col1.addWidget(self.dark_mode)

        btn_row1 = QHBoxLayout()
        btn_row2 = QHBoxLayout()
        
        btn_row1.addWidget(self.add_btn)
        btn_row1.addWidget(self.del_btn)
        btn_row2.addWidget(self.submit_btn)
        btn_row2.addWidget(self.clear_btn)
        self.col1.addLayout(btn_row1)
        self.col1.addLayout(btn_row2)
        
        self.col2.addWidget(self.canvas)
        self.col2.addWidget(self.table)
        
        
        self.master_layout.addLayout(self.col1,30)
        self.master_layout.addLayout(self.col2, 70)
        
        self.setLayout(self.master_layout)
        
        
        
        self.add_btn.clicked.connect(self.add_workout)
        self.del_btn.clicked.connect(self.delete_workout)
        self.submit_btn.clicked.connect(self.submit_clicked)
        self.clear_btn.clicked.connect(self.reset)
        self.dark_mode.stateChanged.connect(self.toggle_dark_mode)
        
        self.load_data()
        self.apply_styles()
        
        
    def load_data(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM fitness ORDER BY date DESC")
        row = 0
        while query.next():
            fit_id = query.value(0)
            date = query.value(1)
            calories = query.value(2)
            distance = query.value(3)
            description = query.value(4)
            
            self.table.insertRow(row)
            self.table.setItem(row,0,QTableWidgetItem(str(fit_id)))
            self.table.setItem(row,1,QTableWidgetItem(date))
            self.table.setItem(row,2,QTableWidgetItem(str(calories)))
            self.table.setItem(row,3,QTableWidgetItem(str(distance)))
            self.table.setItem(row,4,QTableWidgetItem(description))
            
            row +=1
        
        
    def add_workout(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        calories = self.kal_box.text()
        distance = self.dist_box.text()
        description = self.description.text()
        
        query = QSqlQuery()
        query.prepare("""
                      INSERT INTO fitness (date,calories,distance,description)
                      VALUES (?,?,?,?)
                      """)
        query.addBindValue(date)
        query.addBindValue(calories)
        query.addBindValue(distance)
        query.addBindValue(description)
        query.exec_()
        
        self.date_box.setDate(QDate.currentDate())
        self.kal_box.clear()
        self.dist_box.clear()
        self.description.clear()
        
        self.load_data()
        
    def delete_workout(self):
        selected_row = self.table.currentRow()
        
        if selected_row == -1:
            QMessageBox.warning(self,"Error","You must choose a row to delete")
        
        fit_id = int(self.table.item(selected_row,0).text())
        
        confirm = QMessageBox.question(self,"Are you sure?","Delete this workout?",QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        
        query=QSqlQuery()
        query.prepare("DELETE FROM fitness WHERE id = ?")
        query.addBindValue(fit_id)
        query.exec_()
        
        self.load_data()
        
    def calculate_correlation(self):
        distances = []
        calories = []

        query = QSqlQuery("SELECT distance, calories FROM fitness")
        while query.next():
            distance = query.value(0)
            calorie = query.value(1)
            distances.append(distance)
            calories.append(calorie)

        correlation = np.corrcoef(distances, calories)[0, 1]
        return correlation

    def submit_clicked(self):
        correlation = self.calculate_correlation()

        # Retrieve distance and calories data for plotting
        distances = []
        calories = []
        query = QSqlQuery("SELECT distance, calories FROM fitness ORDER BY calories ASC")
        while query.next():
            distance = query.value(0)
            calorie = query.value(1)
            distances.append(distance)
            calories.append(calorie)

        min_calorie = min(calories)
        max_calorie = max(calories)
        normalized_calories = [(calorie - min_calorie) / (max_calorie - min_calorie) for calorie in calories]

        # Plot the data
        plt.style.use("seaborn-darkgrid")
        ax = self.figure.subplots()
        ax.scatter(distances, calories, c=normalized_calories, cmap='viridis', label='Data Points')
        ax.set_xlabel('Distance')
        ax.set_ylabel('Calories')
        ax.set_title('Distance vs. Calories')
        cbar = ax.figure.colorbar(ax.collections[0], label='Normalized Calories')
        ax.legend()
        self.canvas.draw()

    def apply_styles(self):
        # Set background colors
        self.setStyleSheet("""
            QWidget {
                background-color: #b8c9e1;
            }
            
            QLabel {
                color: #333;
                font-size: 14px;
            }
            
            QLineEdit, QComboBox, QDateEdit, QPushButton {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                padding: 5px;
            }
            
            QTableWidget {
                background-color: #b8c9e1;
                color: #333;
                border: 1px solid #444;
                selection-background-color: #ddd;
            }
            
            QPushButton {
                background-color: #4caf50;
                color: #fff;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            
        """)
        figure_color = "#b8c9e1"
        self.figure.patch.set_facecolor(figure_color)
        self.canvas.setStyleSheet(f"background-color: {figure_color};")

        # Set dark mode styles
        if self.dark_mode.isChecked():
            self.setStyleSheet(
                """
                FitnessApp {
                    background-color: #222222;
                }

                QLineEdit, QPushButton, QDateEdit {
                    background-color:#222222;
                    color: #eeeeee;
                    border: 1px solid #444;
                    padding: 5px;
                }
                QLabel{
                     background-color:#222222;
                    color: #eeeeee;
                    padding: 5px;
                }

                QTableWidget {
                    background-color: #444444;
                    color: #eeeeee;
                }
                
                QCheckBox{
                    color: #eeeeee;
                }
                QPushButton {
                background-color: #40484c;
                color: #fff;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            
                QPushButton:hover {
                    background-color: #444d4f;
                }
                """
            )
            figure_color = "#40484c"
            self.figure.patch.set_facecolor(figure_color)
            self.canvas.setStyleSheet(f"background-color: {figure_color};")
            
            # Add code to change chart color here!

    def toggle_dark_mode(self):
        self.apply_styles()
        

            
        
    def reset(self):
        self.date_box.setDate(QDate.currentDate())
        self.description.clear()
        self.kal_box.clear()
        self.dist_box.clear()
        self.figure.clear()
        self.canvas.draw()
        
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("fitness.db")
if not db.open():
    QMessageBox.critical(None, "Error","Can not open database!")
    exit(2)
        
query = QSqlQuery()
query.exec_("""
            CREATE TABLE IF NOT EXISTS fitness (
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                calories REAL,
                distance REAL,
                description TEXT
            )
            """)

if __name__ in "__main__":
    app = QApplication([])
    main = FitnessApp()
    main.show()
    app.exec_()
        
        
import sys
import os
import subprocess
import psutil
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Server:
    def __init__(self, name, command):
        self.name = name
        self.command = command
        # self.log_location = log_location
        self.process = None
        self.pid = None
        self.port = None
        self.ip = None
        self.status = 'stopped'

    def start(self):
        if self.process is not None:
            return
        self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.pid = self.process.pid
        self.port = '-'
        self.ip = '-'
        self.status = 'running'

    def stop(self):
        if self.process is None:
            return
        self.process.terminate()
        self.process = None
        self.pid = None
        self.port = None
        self.ip = None
        self.status = 'stopped'

    def is_running(self):
        return self.process is not None and self.process.poll() is None
    
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.servers = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Local Server Manager (LSM)')
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['Name', 'Command', 'Status', 'PID', 'Port', 'IP', 'Actions'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        add_button = QPushButton('Add Server')
        add_button.clicked.connect(self.add_server)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.addWidget(add_button)
        self.setLayout(self.layout)

    def add_server(self):
        dialog = QDialog()
        dialog.setWindowTitle('Add Server')
        dialog.setMinimumWidth(600)

        name_label = QLabel('Name:')
        self.name_input = QLineEdit()

        command_label = QLabel('Command:')
        self.command_input = QLineEdit()

        # log_location_label = QLabel('Log Location:')
        # self.log_location_input = QLineEdit()

        save_button = QPushButton('Save')
        save_button.clicked.connect(dialog.accept)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(dialog.reject)

        layout = QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(self.name_input, 0, 1)
        layout.addWidget(command_label, 1, 0)
        layout.addWidget(self.command_input, 1, 1)
        # layout.addWidget(log_location_label, 2, 0)
        # layout.addWidget(self.log_location_input, 2, 1)
        layout.addWidget(save_button, 3, 0)
        layout.addWidget(cancel_button, 3, 1)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            name = self.name_input.text()
            command = self.command_input.text()
            # log_location = self.log_location_input.text()

            server = Server(name, command)
            self.servers.append(server)

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(name))
            self.table.setItem(row_position, 1, QTableWidgetItem(command))
            # self.table.setItem(row_position, 2, QTableWidgetItem(log_location))
            self.table.setItem(row_position, 2, QTableWidgetItem(server.status))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(server.pid)))
            self.table.setItem(row_position, 4, QTableWidgetItem(str(server.port)))
            self.table.setItem(row_position, 5, QTableWidgetItem(str(server.ip)))
            

            start_button = QPushButton('Start')
            stop_button = QPushButton('Stop')
            start_button.clicked.connect(lambda: self.start_server(server))
            stop_button.clicked.connect(lambda: self.stop_server(server))
            layout = QHBoxLayout()
            layout.addWidget(start_button)
            layout.addWidget(stop_button)

            container_widget = QWidget()
            container_widget.setLayout(layout)

            self.table.setCellWidget(row_position, 6, container_widget)

    def start_server(self, server):
        # Import subprocess module to run server commands
        import subprocess

        # Split command into list of arguments
        cmd_args = server.command.split()

        # Run server command in background with no terminal output
        process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Update server status in table
        index = self.servers.index(server)
        self.servers[index].pid = process.pid
        time.sleep(3)
        
        #####
        _pid = process.pid
        p = psutil.Process(int(_pid))
        conns = p.connections()
        if len(conns)>0:
            _ip, _port = conns[0].laddr.ip, conns[0].laddr.port
            self.servers[index].ip = _ip
            self.servers[index].port = _port
        #####
        
        self.servers[index].status = "Running"
        # row = self.table.row(index)
        self.table.setItem(index, 2, QTableWidgetItem(self.servers[index].status))
        self.table.setItem(index, 3, QTableWidgetItem(str(self.servers[index].pid)))
        self.table.setItem(index, 4, QTableWidgetItem(str(self.servers[index].port)))
        self.table.setItem(index, 5, QTableWidgetItem(str(self.servers[index].ip)))

    def stop_server(self, server):
        # Import os module to send SIGTERM signal to process
        import os

        # Send SIGTERM signal to server process using kill command
        os.kill(server.pid, 15)

        # Update server status in table
        index = self.servers.index(server)
        self.servers[index].pid = None
        self.servers[index].port = None
        self.servers[index].ip = None
        self.servers[index].status = "Stopped"
        # row = self.table.row(index)
        self.table.setItem(index, 2, QTableWidgetItem(self.servers[index].status))
        self.table.setItem(index, 3, QTableWidgetItem(str(self.servers[index].pid)))
        self.table.setItem(index, 4, QTableWidgetItem(str(self.servers[index].port)))
        self.table.setItem(index, 5, QTableWidgetItem(str(self.servers[index].ip)))
        
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
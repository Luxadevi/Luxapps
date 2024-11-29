# /// script
# dependencies = [
#   "toml",
#   "tcl",
#   "tk",
#   "PyQt5",
#   "sshfs",
# ]
# ///
import sys
import os
import subprocess
import toml
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QInputDialog,
    QLineEdit,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

CONFIG_FILE = "connections.toml"

class SSHFSManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSHFS Connection Manager")
        self.resize(800, 600)

        # Load configuration
        self.config_data = self.read_config()
        self.connections = self.config_data.get("connections", [])

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        # Remove titlebar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Main layout
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("SSHFS Connection Manager")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Connections area
        self.connections_area = QScrollArea()
        self.connections_area.setWidgetResizable(True)
        self.connections_widget = QWidget()
        self.connections_layout = QVBoxLayout()
        self.connections_widget.setLayout(self.connections_layout)
        self.connections_area.setWidget(self.connections_widget)
        self.load_connections()
        layout.addWidget(self.connections_area)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_connection)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        # Set main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Apply Catpuccin theme
        self.apply_catpuccin_theme()

    def apply_catpuccin_theme(self):
        # Apply Catpuccin-like theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 8px;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 16px;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: 1px solid #89b4fa;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 16px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QScrollArea {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                background: #45475a;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #89b4fa;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QFrame {
                background-color: #45475a;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
            QMessageBox {
                background-color: #313244;
                color: #cdd6f4;
            }
            QMessageBox QLabel {
                color: #cdd6f4;
            }
            QMessageBox QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: 1px solid #89b4fa;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 16px;
            }
            QMessageBox QPushButton:hover {
                background-color: #74c7ec;
            }
            QInputDialog {
                background-color: #313244;
                color: #cdd6f4;
            }
            QInputDialog QLabel {
                color: #cdd6f4;
            }
            QInputDialog QLineEdit {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 8px;
                border-radius: 8px;
                font-size: 14px;
            }
            QInputDialog QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: 1px solid #89b4fa;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 16px;
            }
            QInputDialog QPushButton:hover {
                background-color: #74c7ec;
            }
        """)

    def read_config(self):
        """Read the TOML configuration file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return toml.load(f)
            except toml.TomlDecodeError as e:
                QMessageBox.critical(self, "Error", f"Failed to read config: {e}")
        return {"connections": []}

    def write_config(self):
        """Write the TOML configuration file."""
        try:
            with open(CONFIG_FILE, "w") as f:
                toml.dump({"connections": self.connections}, f)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")

    def load_connections(self):
        """Load connections into the card layout."""
        for i in reversed(range(self.connections_layout.count())):
            self.connections_layout.itemAt(i).widget().setParent(None)

        for conn in self.connections:
            card = QFrame()
            card_layout = QVBoxLayout()

            host_label = QLabel(f"Host: {conn['host']}")
            user_label = QLabel(f"User: {conn.get('user', 'root')}")
            remote_dir_label = QLabel(f"Remote Dir: {conn.get('remote_dir', '/root/')}")

            btn_layout = QHBoxLayout()
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, c=conn: self.edit_connection(c))
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, c=conn: self.delete_connection(c))
            mount_btn = QPushButton("Mount")
            mount_btn.clicked.connect(lambda _, c=conn: self.mount_connection(c))

            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.addWidget(mount_btn)

            card_layout.addWidget(host_label)
            card_layout.addWidget(user_label)
            card_layout.addWidget(remote_dir_label)
            card_layout.addLayout(btn_layout)

            card.setLayout(card_layout)
            self.connections_layout.addWidget(card)

    def add_connection(self):
        """Add a new connection."""
        host, ok = QInputDialog.getText(self, "Add Connection", "Enter Host:")
        if not ok or not host.strip():
            return
        user, ok = QInputDialog.getText(self, "Add Connection", "Enter User (default: root):")
        remote_dir, ok = QInputDialog.getText(
            self, "Add Connection", "Enter Remote Dir (default: /root/):"
        )
        connection = {
            "host": host.strip(),
            "user": user.strip() if user.strip() else "root",
            "remote_dir": remote_dir.strip() if remote_dir.strip() else "/root/",
        }
        self.connections.append(connection)
        self.write_config()
        self.load_connections()

    def edit_connection(self, connection):
        """Edit the selected connection."""
        host, ok = QInputDialog.getText(
            self, "Edit Connection", "Enter Host:", QLineEdit.Normal, connection["host"]
        )
        if not ok or not host.strip():
            return
        user, ok = QInputDialog.getText(
            self,
            "Edit Connection",
            "Enter User (default: root):",
            QLineEdit.Normal,
            connection.get("user", "root"),
        )
        remote_dir, ok = QInputDialog.getText(
            self,
            "Edit Connection",
            "Enter Remote Dir (default: /root/):",
            QLineEdit.Normal,
            connection.get("remote_dir", "/root/"),
        )
        connection["host"] = host.strip()
        connection["user"] = user.strip() if user.strip() else "root"
        connection["remote_dir"] = remote_dir.strip() if remote_dir.strip() else "/root/"
        self.write_config()
        self.load_connections()

    def delete_connection(self, connection):
        """Delete the selected connection."""
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the connection to {connection['host']}?",
        )
        if confirm == QMessageBox.Yes:
            self.connections.remove(connection)
            self.write_config()
            self.load_connections()

    def mount_connection(self, connection):
        """Mount the selected connection."""
        host = connection["host"]
        user = connection.get("user", "root")
        remote_dir = connection.get("remote_dir", "/root/")
        mount_point = os.path.expanduser(f"~/mounted/{host}/")

        os.makedirs(mount_point, exist_ok=True)
        cmd = ["sshfs", f"{user}@{host}:{remote_dir}", mount_point]
        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "Success", f"Mounted {host} at {mount_point}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to mount {host}.\n\nCommand:\n{' '.join(cmd)}\n\nError:\n{e}",
            )

def main():
    app = QApplication(sys.argv)
    window = SSHFSManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

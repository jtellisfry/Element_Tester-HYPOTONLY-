"""
Test Passed Dialog Widget

Shows a success screen when both hipot and measurement tests pass.
Displays "PASS" with green styling and a CONTINUE button.
"""
from PyQt6 import QtWidgets, QtCore, QtGui


class TestPassedDialog(QtWidgets.QDialog):
    """Dialog shown when test passes"""
    
    def __init__(self, parent=None, print_callback=None):
        super().__init__(parent)
        self.print_callback = print_callback
        self._print_triggered = False
        self.setWindowTitle("Test Passed")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # PASS label
        pass_label = QtWidgets.QLabel("PASS")
        pass_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        pass_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 72px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        layout.addWidget(pass_label)
        
        # Success icon/checkmark
        check_label = QtWidgets.QLabel("✓")
        check_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        check_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 96px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        layout.addWidget(check_label)
        
        # Success message
        message_label = QtWidgets.QLabel("All tests completed successfully")
        message_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 18px;
                font-weight: 500;
            }
        """)
        layout.addWidget(message_label)
        
        # Spacer
        layout.addStretch()
        
        # Continue button
        continue_btn = QtWidgets.QPushButton("CONTINUE")
        continue_btn.setMinimumHeight(60)
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        continue_btn.clicked.connect(self.accept)
        layout.addWidget(continue_btn)
        
        # Set dialog background
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
        """)
        
        self.setLayout(layout)
    
    def showEvent(self, event):
        """Override showEvent to trigger print 1 second after dialog appears"""
        super().showEvent(event)
        # Only trigger print once
        if self.print_callback and not self._print_triggered:
            self._print_triggered = True
            # Schedule print for 1 second after dialog appears
            QtCore.QTimer.singleShot(1000, self.print_callback)
    
    @staticmethod
    def show_passed(parent=None, work_order: str = "", part_number: str = "", print_callback=None) -> bool:
        """
        Show the test passed dialog.
        
        Args:
            parent: Parent widget
            work_order: Work order number (for printing, if needed)
            part_number: Part number (for printing, if needed)
            print_callback: Optional callback to trigger printing 1 second after dialog appears
        
        Returns:
            True when user clicks CONTINUE
        """
        dialog = TestPassedDialog(parent, print_callback=print_callback)
        result = dialog.exec()
        return result == QtWidgets.QDialog.DialogCode.Accepted
        dialog = TestPassedDialog(parent)
        dialog.open()  # Use open() instead of exec() - non-blocking but still modal
        # Note: open() returns immediately, dialog stays visible until user clicks CONTINUE
        # The accepted/rejected signals will fire when user interacts with dialog
        return True

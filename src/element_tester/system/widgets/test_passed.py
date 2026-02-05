"""
Test Passed Dialog Widget

Shows a success screen when both hipot and measurement tests pass.
Displays "PASS" with green styling and a CONTINUE button.
"""
from PyQt6 import QtWidgets, QtCore, QtGui


class TestPassedDialog(QtWidgets.QDialog):
    """Dialog shown when test passes"""
    
    def __init__(self, parent=None, work_order: str = "", part_number: str = ""):
        super().__init__(parent)
        self.work_order = work_order
        self.part_number = part_number
        self.print_timer = None  # Track timer for cleanup
        self.print_triggered = False  # Ensure print only happens once
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
        """Trigger print when dialog is shown (avoids race conditions with timer)."""
        try:
            super().showEvent(event)
            # Trigger print immediately when dialog becomes visible
            # This ensures print happens while dialog is displayed, not after it's closed
            if not self.print_triggered and self.work_order and self.part_number:
                self.print_triggered = True
                # Use QTimer.singleShot with 0ms to defer to next event loop cycle
                # This ensures dialog is fully rendered before print starts
                QtCore.QTimer.singleShot(100, lambda: self._trigger_print(self.work_order, self.part_number))
        except Exception as e:
            print(f"ERROR in showEvent: {e}")
            import traceback
            traceback.print_exc()
            # Continue showing dialog even if print fails
            super().showEvent(event)
    
    def closeEvent(self, event):
        """Cleanup when dialog closes."""
        # Cancel timer if still pending
        if self.print_timer is not None:
            try:
                self.print_timer.stop()
            except Exception:
                pass
        super().closeEvent(event)
    
    @staticmethod
    def show_passed(parent=None, work_order: str = "", part_number: str = "") -> bool:
        """
        Show the test passed dialog and trigger QC printing.
        
        Args:
            parent: Parent widget
            work_order: Work order number for QC label
            part_number: Part number for QC label
        
        Returns:
            True when user clicks CONTINUE
        """
        dialog = TestPassedDialog(parent, work_order, part_number)
        
        # Print is triggered automatically in showEvent
        result = dialog.exec()
        
        # Give print thread a moment to start before window transitions
        QtCore.QThread.msleep(50)
        
        return result == QtWidgets.QDialog.DialogCode.Accepted
    
    @staticmethod
    def _trigger_print(work_order: str, part_number: str) -> None:
        """Trigger QC label printing in background thread."""
        try:
            from element_tester.system.procedures import print_qc
            import threading
            
            # Run print in background thread to avoid blocking UI
            def print_job():
                try:
                    print_qc.print_message(work_order, part_number)
                except Exception as e:
                    print(f"QC print failed: {e}")
            
            thread = threading.Thread(target=print_job, daemon=True)
            thread.start()
        except Exception as e:
            print(f"Failed to trigger QC print: {e}")

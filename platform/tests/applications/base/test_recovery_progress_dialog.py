import unittest
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton
from PyQt6.QtTest import QTest
from src.applications.base.recovery_progress_dialog import RecoveryProgressDialog


class TestRecoveryProgressDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_existing_fluid_animation_and_complete_text(self):
        dialog = RecoveryProgressDialog(None, "Resetting collision hold",
            "Recalibrating the torque observer. Keep the robot stationary and free of contact. "
            "This usually takes 10–11 seconds. Motion remains held until recovery completes.")
        dialog.show()
        self.app.processEvents()
        self.assertTrue(dialog.progress.running)
        self.assertTrue(dialog.progress.waiting)
        self.assertTrue(dialog.isModal())
        body = dialog.findChild(QLabel, "recoveryProgressMessage")
        self.assertGreaterEqual(body.height(), body.heightForWidth(body.width()))
        self.assertFalse(dialog.findChildren(QPushButton))
        initial_phase = dialog.progress.phase
        QTest.qWait(350)
        self.assertGreater(dialog.progress.phase, initial_phase)
        dialog.grab().save("/tmp/zeroerr-recovery-progress-preview.png")
        dialog.close()
        self.assertFalse(dialog.progress.running)

    def test_bulgarian_message_fits(self):
        dialog = RecoveryProgressDialog(None, "Нулиране на блокировката след сблъсък",
            "Калибриране на наблюдателя на въртящия момент. Дръжте робота неподвижен и без външен контакт. "
            "Това обикновено отнема 10–11 секунди. Движението остава блокирано до завършване на възстановяването.")
        dialog.show()
        self.app.processEvents()
        body = dialog.findChild(QLabel, "recoveryProgressMessage")
        self.assertGreaterEqual(body.height(), body.heightForWidth(body.width()))
        dialog.close()

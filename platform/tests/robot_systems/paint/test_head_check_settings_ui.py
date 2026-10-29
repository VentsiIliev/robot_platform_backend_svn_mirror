"""Human labels translate while saved policy/action identities remain stable."""

import json
import unittest
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QEvent, QTranslator
from PyQt6.QtWidgets import QApplication

from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField
from src.robot_systems.paint.applications.paint_process_settings.mapper import (
    PaintProcessSettingsMapper,
)
from src.robot_systems.paint.applications.paint_process_settings.view.head_check_choices import (
    HeadCheckChoiceCombo,
)
from src.robot_systems.paint.applications.paint_process_settings.view.paint_process_settings_view import (
    PaintProcessSettingsView,
)
from src.robot_systems.paint.paint_head_check.policy_registry import FIRST_THEN_INTERVAL_POLICY
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig


class CatalogTranslator(QTranslator):
    def __init__(self, language: str) -> None:
        super().__init__()
        root = Path(__file__).resolve().parents[3]
        self.catalog = json.loads(
            (root / "src/robot_systems/paint/storage/translations" / f"{language}.json").read_text()
        )

    def isEmpty(self) -> bool:
        return False

    def translate(
        self,
        context: str | None,
        source: str | None,
        disambiguation: str | None = None,
        n: int = -1,
    ) -> str:
        return self.catalog.get(context, {}).get(source, source or "")


class HeadCheckSettingsUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.translator: CatalogTranslator | None = None
        self.addCleanup(self.remove_translator)

    def remove_translator(self) -> None:
        if self.translator is not None:
            self.app.removeTranslator(self.translator)
            self.translator = None

    def install_language(self, language: str) -> None:
        self.remove_translator()
        self.translator = CatalogTranslator(language)
        self.app.installTranslator(self.translator)

    def view(self) -> PaintProcessSettingsView:
        view = PaintProcessSettingsView()
        view.set_values(PaintProcessSettingsMapper.to_flat_dict(PaintProcessConfig()))
        self.addCleanup(self.dispose, view)
        return view

    def dispose(self, view: PaintProcessSettingsView) -> None:
        view.clean_up()
        view.close()
        view.deleteLater()
        self.app.processEvents()

    def test_initial_bulgarian_labels_keep_the_same_saved_ids(self) -> None:
        self.install_language("bg")
        view = self.view()
        combo = view.findChild(HeadCheckChoiceCombo, "head_check_policy_id")
        self.assertIsNotNone(combo)
        self.assertEqual("Всеки цикъл", combo.currentText())
        self.assertEqual("every_cycle", view.values()["head_check_policy_id"])
        action = view.findChild(HeadCheckChoiceCombo, "head_check_missing_action")
        self.assertEqual("Спиране на процеса (Старт за нова проверка)", action.currentText())
        self.assertEqual("stop", action.currentData())

    def test_runtime_switch_retains_policy_interval_and_timeout(self) -> None:
        self.install_language("en")
        view = self.view()
        values = view.values()
        values.update(
            {
                "head_check_policy_id": FIRST_THEN_INTERVAL_POLICY.value,
                "head_check_interval_cycles": 5,
                "head_check_timeout_seconds": 2.5,
            }
        )
        view.set_values(values)
        self.install_language("bg")
        QApplication.sendEvent(view, QEvent(QEvent.Type.LanguageChange))
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.app.processEvents()
        combo = view.findChild(HeadCheckChoiceCombo, "head_check_policy_id")
        current = view.values()
        self.assertEqual(FIRST_THEN_INTERVAL_POLICY.value, current["head_check_policy_id"])
        self.assertEqual(5, current["head_check_interval_cycles"])
        self.assertEqual(2.5, current["head_check_timeout_seconds"])
        self.assertEqual("Първият цикъл, след това през N цикъла", combo.currentText())

    def test_interval_uses_shared_numeric_field_and_follows_policy_selection(self) -> None:
        self.install_language("en")
        view = self.view()
        field = view.findChild(KeyboardNumberField, "head_check_interval_cycles")
        self.assertIsNotNone(field)
        self.assertTrue(field.parentWidget().isHidden())
        combo = view.findChild(HeadCheckChoiceCombo, "head_check_policy_id")
        combo.setCurrentIndex(combo.findData(FIRST_THEN_INTERVAL_POLICY.value))
        self.assertFalse(field.parentWidget().isHidden())
        field.setValue(7)
        self.assertEqual(7, view.values()["head_check_interval_cycles"])


if __name__ == "__main__":
    unittest.main()

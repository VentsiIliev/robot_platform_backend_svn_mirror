import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch

from PyQt6 import sip
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import QApplication, QColorDialog, QPushButton

from pl_gui.theme.palette import DEFAULT_COLORS, THEME_PRESETS, theme_palette
from pl_gui.theme.runtime import install_theme
from pl_gui.theme.icon import themed_icon
from pl_gui.shell.ui.LanguageSelectorWidget import LanguageSelectorWidget
from pl_gui.utils.utils_widgets.SwitchButton import QToggle
from src.applications.platform_settings.platform_settings_factory import PlatformSettingsFactory
from src.applications.platform_settings.service.platform_settings_service import PlatformSettingsService
from src.engine.localization.localization_service import LocalizationService


class AppearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        install_theme(cls.app)

    def setUp(self):
        self.original = theme_palette.colors()
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'ui.json'
        self.service = PlatformSettingsService(self.path)
        self.widgets = []

    def tearDown(self):
        for widget in self.widgets:
            if not sip.isdeleted(widget):
                sip.delete(widget)
        theme_palette.set_colors(self.original)
        self.app.processEvents()
        self.temp.cleanup()

    def button(self):
        button = QPushButton()
        self.widgets.append(button)
        button.setStyleSheet('background: #905BA9; color: white; border: 1px solid #E0E0E0;')
        return button

    def test_live_repeated_updates_new_widgets_dynamic_styles_and_reset(self):
        existing = self.button()
        existing.show()
        self.app.processEvents()
        self.service.set_colors({'primary': '#112233', 'surface': '#AAAAAA'})
        self.app.processEvents()
        self.assertIn('#112233', existing.styleSheet())
        self.assertIn('color: white', existing.styleSheet())
        self.assertIn('#112233', self.button().styleSheet())
        existing.setStyleSheet(existing.styleSheet() + ' padding: 8px;')
        self.service.set_colors({'primary': '#445566'})
        self.app.processEvents()
        self.assertIn('#445566', existing.styleSheet())
        self.assertIn('padding: 8px', existing.styleSheet())
        existing.setStyleSheet('color: #905BA9;')
        self.assertEqual(existing.styleSheet(), 'color: #445566;')
        self.service.set_colors(DEFAULT_COLORS)
        self.app.processEvents()
        self.assertEqual(existing.styleSheet(), 'color: #905BA9;')
        self.assertEqual(PlatformSettingsService(self.path).get_colors(), DEFAULT_COLORS)

    def test_invalid_values_and_failed_save_do_not_change_active_theme(self):
        self.path.write_text(json.dumps({'ui': {'fullscreen': True}, 'robot_system': 'paint'}))
        before = self.path.read_text()
        for bad in ({'primary': 'red; background: black'}, {'missing': '#123456'}, {'text': None}):
            with self.assertRaises(ValueError):
                self.service.set_colors(bad)
        self.assertEqual(self.path.read_text(), before)
        with patch.object(self.service, '_atomic_write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.service.set_colors({'primary': '#123456'})
        self.assertEqual(theme_palette.colors(), self.original)
        self.service.set_colors({'primary': '#123456'})
        saved = json.loads(self.path.read_text())
        self.assertTrue(saved['ui']['fullscreen'])
        self.assertEqual(saved['robot_system'], 'paint')

    def test_cached_icons_and_custom_painted_toggle_follow_palette(self):
        def icon_factory(color):
            pixmap = QPixmap(8, 8)
            pixmap.fill(QColor(color))
            return QIcon(pixmap)
        icon = themed_icon(icon_factory, '#905BA9')
        toggle = QToggle()
        self.widgets.append(toggle)
        toggle.sync_visual_state(True)
        self.service.set_colors({'primary': '#123456'})
        self.app.processEvents()
        self.assertEqual(icon.pixmap(QSize(8, 8)).toImage().pixelColor(0, 0).name(), '#123456')
        self.assertEqual(toggle.active_color.name(), '#123456')
        self.assertEqual(toggle.intermediate_bg_color.name(), '#123456')
        sip.delete(toggle)
        self.service.set_colors({'primary': '#654321'})

    def test_preview_does_not_write_apply_commits_and_discard_restores(self):
        self.service.set_colors(DEFAULT_COLORS)
        saved = self.path.read_text()
        self.service.preview_colors({'primary': '#123456'})
        self.assertEqual(theme_palette.colors()['primary'], '#123456')
        self.assertEqual(self.path.read_text(), saved)
        self.service.discard_color_preview()
        self.assertEqual(theme_palette.colors(), DEFAULT_COLORS)
        self.service.preview_colors({'primary': '#123456'})
        with patch.object(self.service, '_atomic_write', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                self.service.set_colors({'primary': '#123456'})
        self.assertEqual(theme_palette.colors()['primary'], '#123456')
        self.assertEqual(self.path.read_text(), saved)
        self.service.set_colors({'primary': '#123456'})
        self.service.preview_colors({'primary': '#ABCDEF'})
        self.service.discard_color_preview()
        self.assertEqual(theme_palette.colors()['primary'], '#123456')
        self.assertEqual(self.service.get_colors()['primary'], '#123456')

    def test_picker_previews_while_open_cancel_rolls_back_apply_is_only_save(self):
        self.service.set_colors(DEFAULT_COLORS)
        view = PlatformSettingsFactory().build(self.service)
        self.widgets.append(view)
        field = view._color_fields['primary']
        saved = self.path.read_text()

        def cancel(dialog):
            for color in ('#123456', '#ABCDEF'):
                dialog.setCurrentColor(QColor(color))
                self.assertEqual(theme_palette.colors()['primary'], color)
                self.assertEqual(self.path.read_text(), saved)
            return QColorDialog.DialogCode.Rejected

        with patch.object(QColorDialog, 'exec', cancel):
            field._choose()
        self.assertEqual(theme_palette.colors(), DEFAULT_COLORS)
        self.assertEqual(field.color(), DEFAULT_COLORS['primary'])

        def accept(dialog):
            dialog.setCurrentColor(QColor('#123456'))
            dialog.accept()
            return QColorDialog.DialogCode.Accepted

        with patch.object(QColorDialog, 'exec', accept):
            field._choose()
        self.assertEqual(theme_palette.colors()['primary'], '#123456')
        self.assertEqual(self.path.read_text(), saved)
        view._apply_colors.click()
        self.assertEqual(self.service.get_colors()['primary'], '#123456')
        # Defaults are a draft, and leaving the page discards them.
        saved = self.path.read_text()
        view._reset_colors.click()
        self.assertEqual(theme_palette.colors(), DEFAULT_COLORS)
        self.assertEqual(self.path.read_text(), saved)
        view.clean_up()
        self.assertEqual(theme_palette.colors()['primary'], '#123456')

    def test_typing_valid_hex_previews_without_saving_and_destruction_discards(self):
        self.service.set_colors(DEFAULT_COLORS)
        saved = self.path.read_text()
        view = PlatformSettingsFactory().build(self.service)
        self.widgets.append(view)
        field = view._color_fields['border']._input
        field.selectAll()
        field.insert('#12')
        self.assertEqual(theme_palette.colors(), DEFAULT_COLORS)
        field.insert('3456')
        self.assertEqual(theme_palette.colors()['border'], '#123456')
        self.assertEqual(self.path.read_text(), saved)
        sip.delete(view)
        self.assertEqual(theme_palette.colors(), DEFAULT_COLORS)

    def test_hiding_cached_page_discards_and_reopening_can_preview_again(self):
        self.service.set_colors(DEFAULT_COLORS)
        view = PlatformSettingsFactory().build(self.service)
        self.widgets.append(view)
        view.show()
        self.app.processEvents()
        field = view._color_fields['primary']
        field._input.selectAll()
        field._input.insert('#123456')
        self.assertEqual(theme_palette.colors()['primary'], '#123456')
        view.hide()
        self.assertEqual(theme_palette.colors(), DEFAULT_COLORS)
        self.assertEqual(field.color(), DEFAULT_COLORS['primary'])
        view.show()
        field._input.selectAll()
        field._input.insert('#654321')
        self.assertEqual(theme_palette.colors()['primary'], '#654321')
        view._apply_colors.click()
        view.hide()
        self.assertEqual(theme_palette.colors()['primary'], '#654321')
        self.assertEqual(self.service.get_colors()['primary'], '#654321')

    def test_theme_presets_preview_apply_reload_and_allow_customization(self):
        self.service.set_colors(DEFAULT_COLORS)
        saved = self.path.read_text()
        view = PlatformSettingsFactory().build(self.service)
        self.widgets.append(view)
        view.show()
        self.assertEqual(view._theme_selector.currentData(), 'light')
        view._theme_selector.setCurrentIndex(view._theme_selector.findData('dark'))
        self.assertEqual(theme_palette.colors(), THEME_PRESETS['dark'])
        self.assertEqual(self.path.read_text(), saved)
        self.assertEqual(view._color_fields['surface'].color(), THEME_PRESETS['dark']['surface'])
        view.hide()
        self.assertEqual(theme_palette.colors(), DEFAULT_COLORS)
        self.assertEqual(view._theme_selector.currentData(), 'light')
        view.show()
        view._theme_selector.setCurrentIndex(view._theme_selector.findData('dark'))
        view._apply_colors.click()
        self.assertEqual(PlatformSettingsService(self.path).get_colors(), THEME_PRESETS['dark'])
        saved = self.path.read_text()
        field = view._color_fields['border']._input
        field.selectAll()
        field.insert('#645A70')
        self.assertEqual(view._theme_selector.currentData(), 'custom')
        self.assertEqual(self.path.read_text(), saved)
        view.hide()
        self.assertEqual(theme_palette.colors(), THEME_PRESETS['dark'])
        self.assertEqual(view._theme_selector.currentData(), 'dark')

    def test_dark_mode_styles_native_palette_and_light_round_trip(self):
        button = self.button()
        source = 'background: white; color: black; border: 1px solid #E0E0E0;'
        button.setStyleSheet(source)
        self.service.set_colors(THEME_PRESETS['dark'])
        self.app.processEvents()
        self.assertIn(THEME_PRESETS['dark']['surface'], button.styleSheet())
        self.assertIn(THEME_PRESETS['dark']['text'], button.styleSheet())
        self.assertEqual(self.app.palette().color(QPalette.ColorRole.Base).name().upper(), THEME_PRESETS['dark']['surface'])
        self.assertLess(self.app.palette().color(QPalette.ColorRole.AlternateBase).value(), 90)
        self.assertGreater(self.app.palette().color(QPalette.ColorRole.PlaceholderText).value(), 140)
        self.assertNotEqual(theme_palette.resolve('#EDE7F6'), '#EDE7F6')
        self.assertNotEqual(theme_palette.resolve('#7D5260'), '#7D5260')
        self.service.set_colors(THEME_PRESETS['light'])
        self.app.processEvents()
        self.assertEqual(button.styleSheet(), source)
        self.assertFalse(theme_palette.is_dark())

    def test_dark_shell_background_and_native_shutdown(self):
        # A separate interpreter exercises native Qt teardown, including a live
        # preview and cached icons, rather than hiding destruction errors.
        script = textwrap.dedent('''
            from PyQt6.QtWidgets import QApplication
            from pl_gui.shell.AppShell import AppShell
            from pl_gui.theme.palette import THEME_PRESETS
            from src.applications.platform_settings.platform_settings_factory import PlatformSettingsFactory
            from src.applications.platform_settings.service.stub_platform_settings_service import StubPlatformSettingsService
            from src.applications.user_management.view.user_management_view import UserManagementView
            from src.applications.user_management.view.permissions_view import PermissionsView
            from src.applications.user_management.domain.default_schema import DEFAULT_USER_SCHEMA
            app = QApplication([])
            view = PlatformSettingsFactory().build(StubPlatformSettingsService())
            shell = AppShell([], lambda _: view, languages=[('en', 'English')])
            shell.resize(1280, 1024)
            shell.show_app('PlatformSettings')
            shell.header.menu_button.show()
            shell.header.power_toggle_button.show()
            shell.show()
            app.processEvents()
            view._theme_selector.setCurrentIndex(view._theme_selector.findData('dark'))
            app.processEvents()
            image = view.grab().toImage()
            assert image.pixelColor(view.width() - 5, 10).name().upper() == THEME_PRESETS['dark']['background']
            shell.grab()
            users = UserManagementView(DEFAULT_USER_SCHEMA)
            permissions = PermissionsView()
            permissions.set_permissions(['dashboard'], ['Admin'], {'dashboard': ['Admin']})
            users.add_permissions_tab(permissions)
            users._tabs.setCurrentIndex(1)
            users.resize(1280, 900)
            users.show()
            app.processEvents()
            users.grab()
        ''')
        result = subprocess.run(
            [sys.executable, '-B', '-c', script],
            cwd=Path(__file__).resolve().parents[3],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_language_controls_sync_translate_and_persist(self):
        catalogs = Path(__file__).resolve().parents[3] / 'src/applications/platform_settings/localization'
        localization = LocalizationService(str(catalogs), state_file=str(Path(self.temp.name) / 'language.json'))
        localization.set_language('en')
        self.service = PlatformSettingsService(self.path, localization_service=localization)
        header_selector = LanguageSelectorWidget(localization.available_languages())
        self.widgets.append(header_selector)
        localization.sync_selector(header_selector)
        header_selector.languageChanged.connect(localization.set_language)
        view = PlatformSettingsFactory().build(self.service)
        self.widgets.append(view)
        view.show()
        self.app.processEvents()
        self.assertEqual(view._language_label.text(), 'Language')
        view._language_selector.setCurrentIndex(view._language_selector.findData('bg'))
        self.app.processEvents()
        self.assertEqual(localization.get_language(), 'bg')
        self.assertEqual(header_selector.current_language, 'bg')
        self.assertEqual(view._language_label.text(), 'Език')
        self.assertEqual(view._apply_colors.text(), 'Прилагане на цветовете')
        self.assertEqual(view._theme_selector.itemText(view._theme_selector.findData('dark')), 'Тъмна')
        reloaded = LocalizationService(str(catalogs), state_file=str(Path(self.temp.name) / 'language.json'))
        self.assertEqual(reloaded.get_language(), 'bg')
        header_selector.setCurrentIndex(header_selector.findText('English'))
        self.app.processEvents()
        self.assertEqual(view._language_selector.currentData(), 'en')
        # Initial rendering after a language was already selected is a separate path.
        localization.set_language('bg')
        second = PlatformSettingsFactory().build(self.service)
        self.widgets.append(second)
        self.assertEqual(second._language_label.text(), 'Език')
        self.assertEqual(second._language_selector.currentData(), 'bg')
        localization.set_language('en')
        if localization._current_translator:
            self.app.removeTranslator(localization._current_translator)


if __name__ == '__main__':
    unittest.main()

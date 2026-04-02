# ui/close_dialog.py
"""
WinUI диалог выбора варианта закрытия приложения.
Показывается при нажатии на крестик (X) в titlebar.
"""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QHBoxLayout

try:
    import qtawesome as qta
    _HAS_QTA = True
except ImportError:
    qta = None
    _HAS_QTA = False
from qfluentwidgets import (
    MessageBoxBase, SubtitleLabel, BodyLabel,
    PushButton, PrimaryPushButton, TransparentPushButton,
)


class CloseDialog(MessageBoxBase):
    """
    WinUI диалог: варианты закрытия приложения.

    Результат через ask_close_action():
      - None    -> отмена (Esc / клик мимо)
      - "tray"  -> свернуть в трей
      - False   -> закрыть только GUI
      - True    -> закрыть GUI + остановить DPI
    """

    def __init__(self, parent=None):
        if parent and not parent.isWindow():
            parent = parent.window()
        super().__init__(parent)
        self.result_stop_dpi = None
        self.result_tray = False

        # --- Заголовок и описание ---
        self.titleLabel = SubtitleLabel("Закрыть приложение", self.widget)
        self.bodyLabel = BodyLabel(
            "DPI обход (winws) продолжит работать в фоне,\n"
            "если вы закроете только GUI.",
            self.widget,
        )
        self.bodyLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.bodyLabel)
        self.viewLayout.addSpacing(8)

        # --- Кнопка "Свернуть в трей" ---
        self.trayButton = PushButton(self.widget)
        self.trayButton.setText("Свернуть в трей")
        self.trayButton.setMinimumHeight(36)
        self._apply_button_icon(self.trayButton, "fa5s.window-restore", "#60cdff", left_aligned=True)
        self.trayButton.clicked.connect(self._on_tray)
        self.viewLayout.addWidget(self.trayButton)

        # --- Кнопка "Закрыть только GUI" ---
        self.guiOnlyButton = PushButton(self.widget)
        self.guiOnlyButton.setText("Закрыть только GUI")
        self.guiOnlyButton.setMinimumHeight(36)
        self._apply_button_icon(self.guiOnlyButton, "fa5s.sign-out-alt", "#aaaaaa", left_aligned=True)
        self.guiOnlyButton.clicked.connect(self._on_gui_only)
        self.viewLayout.addWidget(self.guiOnlyButton)

        # --- Кнопка "Закрыть и остановить DPI" (danger/red) ---
        self.stopDpiButton = PushButton(self.widget)
        self.stopDpiButton.setText("Закрыть и остановить DPI")
        self.stopDpiButton.setMinimumHeight(36)
        self.stopDpiButton.setStyleSheet(
            "QPushButton{background-color:#c42b1c;color:white;border:none;border-radius:5px;"
            "}"
            "QPushButton:hover{background-color:#a52014;}"
            "QPushButton:pressed{background-color:#8e1a10;}"
        )
        self._apply_button_icon(self.stopDpiButton, "fa5s.stop-circle", "#ffffff", left_aligned=True)
        self.stopDpiButton.clicked.connect(self._on_stop_dpi)
        self.viewLayout.addWidget(self.stopDpiButton)

        # --- Кнопка "Отмена" (прозрачная, по центру) ---
        self._cancelRow = QHBoxLayout()
        self._cancelRow.addStretch()
        self.cancelLinkButton = TransparentPushButton(self.widget)
        self.cancelLinkButton.setText("Отмена")
        self._apply_button_icon(self.cancelLinkButton, "fa5s.times", "#aaaaaa")
        self.cancelLinkButton.clicked.connect(self.reject)
        self._cancelRow.addWidget(self.cancelLinkButton)
        self._cancelRow.addStretch()
        self.viewLayout.addLayout(self._cancelRow)

        # Скрываем дефолтные кнопки MessageBoxBase и убираем их пространство
        self.yesButton.hide()
        self.cancelButton.hide()
        self.buttonGroup.setFixedHeight(0)

        self.widget.setMinimumWidth(380)

    def _append_button_style(self, button, qss: str) -> None:
        try:
            base_style = str(button.styleSheet() or "")
            if qss not in base_style:
                button.setStyleSheet(base_style + qss)
        except Exception:
            pass

    def _apply_left_aligned_button_layout(self, button) -> None:
        # Оставляем заметный запас слева, чтобы иконка не наезжала на длинный текст.
        self._append_button_style(
            button,
            "QPushButton{text-align:left;padding-left:42px;padding-right:16px;}",
        )

    def _apply_button_icon(self, button, icon_name: str, color: str, *, left_aligned: bool = False) -> None:
        try:
            button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            button.setIconSize(QSize(16, 16))
        except Exception:
            pass
        if left_aligned:
            self._apply_left_aligned_button_layout(button)
        if not _HAS_QTA:
            return
        try:
            button.setIcon(qta.icon(icon_name, color=color))
        except Exception:
            pass

    def _on_tray(self):
        self.result_tray = True
        self.accept()

    def _on_gui_only(self):
        self.result_stop_dpi = False
        self.accept()

    def _on_stop_dpi(self):
        self.result_stop_dpi = True
        self.accept()


class StartStrategyWarningDialog(MessageBoxBase):
    """WinUI warning-диалог о том, что стратегия не выбрана."""

    def __init__(self, parent=None, title: str = "Стратегия не выбрана", subtitle: str = ""):
        if parent and not parent.isWindow():
            parent = parent.window()
        super().__init__(parent)

        subtitle_text = subtitle or (
            "Для запуска Zapret выберите хотя бы одну стратегию "
            "в разделе «Стратегии»."
        )

        self.titleLabel = SubtitleLabel(title, self.widget)
        self.bodyLabel = BodyLabel(subtitle_text, self.widget)
        self.bodyLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.bodyLabel)

        self.yesButton.setText("Понятно")
        self.hideCancelButton()

        self.widget.setMinimumWidth(380)


def show_start_strategy_warning(parent=None, subtitle: str = "") -> None:
    """Показывает предупреждение о необходимости выбрать стратегию."""
    dlg = StartStrategyWarningDialog(parent=parent, subtitle=subtitle)
    dlg.exec()


def ask_close_action(parent=None):
    """
    Возвращает действие закрытия приложения:
      - None   -> пользователь отменил
      - "tray" -> свернуть в трей
      - False  -> закрыть только GUI
      - True   -> закрыть GUI + остановить DPI

    Если DPI-процесс не запущен, диалог не показывается и
    сразу возвращается False (закрыть только GUI).
    """
    is_dpi_running = True

    try:
        dpi_controller = getattr(parent, "dpi_controller", None)
        if dpi_controller and hasattr(dpi_controller, "is_running"):
            is_dpi_running = bool(dpi_controller.is_running())
    except Exception:
        pass

    if is_dpi_running and parent is not None:
        try:
            dpi_starter = getattr(parent, "dpi_starter", None)
            if dpi_starter and hasattr(dpi_starter, "check_process_running_wmi"):
                is_dpi_running = bool(dpi_starter.check_process_running_wmi(silent=True))
        except Exception:
            pass

    if not is_dpi_running:
        return False

    dlg = CloseDialog(parent)
    dlg.exec()
    if dlg.result_tray:
        return "tray"
    return dlg.result_stop_dpi

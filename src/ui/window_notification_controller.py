from __future__ import annotations

import time

from PyQt6.QtCore import Q_ARG, QMetaObject, QObject, Qt, QTimer, pyqtSlot
from PyQt6.QtWidgets import QApplication

from log import global_logger, log


class WindowNotificationController(QObject):
    """Единый контроллер верхнеуровневых уведомлений приложения."""

    def __init__(self, host) -> None:
        super().__init__(host)
        self.host = host
        self._startup_notification_queue: list[dict] = []
        self._startup_notification_timer = QTimer(self)
        self._startup_notification_timer.setSingleShot(True)
        self._startup_notification_timer.timeout.connect(self.flush_startup_notification_queue)

        self._last_launch_error_message = ""
        self._last_launch_error_ts = 0.0
        self._last_launch_warning_message = ""
        self._last_launch_warning_ts = 0.0

    def register_global_error_notifier(self) -> None:
        """Подключает глобальные ERROR/CRITICAL логи к верхнему InfoBar."""
        try:
            if hasattr(global_logger, "set_ui_error_notifier"):
                global_logger.set_ui_error_notifier(self.enqueue_global_error_infobar)
        except Exception as e:
            log(f"Ошибка подключения глобального error-notifier: {e}", "DEBUG")

    def enqueue_global_error_infobar(self, message: str) -> None:
        """Thread-safe постановка ошибки в GUI очередь."""
        text = str(message or "").strip()
        if not text:
            return

        try:
            QMetaObject.invokeMethod(
                self,
                "show_launch_error",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, text),
            )
        except Exception:
            try:
                self.show_launch_error(text)
            except Exception:
                pass

    @pyqtSlot(str)
    def show_launch_error(self, message: str) -> None:
        import re as _re

        text = str(message or "").strip()
        if not text:
            text = "Не удалось запустить DPI"

        auto_fix_action: str | None = None
        match = _re.match(r"^\[AUTOFIX:(\w+)]", text)
        if match:
            auto_fix_action = match.group(1)
            text = text[match.end():]

        try:
            now = time.time()
            if text == self._last_launch_error_message and (now - self._last_launch_error_ts) < 1.5:
                return
            self._last_launch_error_message = text
            self._last_launch_error_ts = now
        except Exception:
            pass

        try:
            from qfluentwidgets import InfoBar as _InfoBar, InfoBarPosition as _IBPos

            duration = -1 if auto_fix_action else 10000

            bar = _InfoBar.error(
                title="Ошибка",
                content=text,
                orient=Qt.Orientation.Vertical if len(text) > 90 else Qt.Orientation.Horizontal,
                isClosable=True,
                position=_IBPos.TOP,
                duration=duration,
                parent=self.host,
            )

            if auto_fix_action and bar is not None:
                self._add_autofix_button(bar, auto_fix_action)
        except Exception as e:
            log(f"Ошибка показа InfoBar запуска DPI: {e}", "DEBUG")

    @pyqtSlot(str)
    def show_launch_warning(self, message: str) -> None:
        text = str(message or "").strip()
        if not text:
            return

        try:
            now = time.time()
            if text == self._last_launch_warning_message and (now - self._last_launch_warning_ts) < 1.5:
                return
            self._last_launch_warning_message = text
            self._last_launch_warning_ts = now
        except Exception:
            pass

        try:
            from qfluentwidgets import InfoBar as _InfoBar, InfoBarPosition as _IBPos

            _InfoBar.warning(
                title="Предупреждение",
                content=text,
                orient=Qt.Orientation.Vertical if len(text) > 90 else Qt.Orientation.Horizontal,
                isClosable=True,
                position=_IBPos.TOP,
                duration=9000,
                parent=self.host,
            )
        except Exception as e:
            log(f"Ошибка показа warning InfoBar запуска DPI: {e}", "DEBUG")

    def copy_to_clipboard_with_feedback(self, text: str, *, label: str = "Текст") -> None:
        try:
            clipboard = QApplication.clipboard()
            if clipboard is None:
                raise RuntimeError("Буфер обмена недоступен")
            clipboard.setText(str(text or ""))
            self.show_launch_warning(f"{label} скопирован в буфер обмена")
        except Exception as e:
            log(f"Не удалось скопировать в буфер обмена: {e}", "DEBUG")
            self.show_launch_warning(f"Не удалось скопировать {label.lower()}")

    def enqueue_startup_notification(self, payload: dict | None) -> None:
        if not payload:
            return

        if self.can_show_startup_notification_now():
            QTimer.singleShot(0, lambda data=dict(payload): self.show_startup_notification(data))
            return

        self._startup_notification_queue.append(dict(payload))
        self.schedule_startup_notification_queue()

    def can_show_startup_notification_now(self) -> bool:
        if not bool(getattr(self.host, "_startup_post_init_ready", False)):
            return False
        if not bool(getattr(self.host, "_startup_background_init_started", False)):
            return False
        try:
            return bool(self.host.isVisible())
        except Exception:
            return False

    def schedule_startup_notification_queue(self, delay_ms: int = 0) -> None:
        if self._startup_notification_timer.isActive():
            return
        self._startup_notification_timer.start(max(0, int(delay_ms)))

    def show_startup_notification(self, payload: dict) -> None:
        try:
            from qfluentwidgets import InfoBar as _InfoBar, InfoBarPosition as _IBPos, PushButton

            level = str(payload.get("level") or "warning").strip().lower()
            title = str(payload.get("title") or "Предупреждение").strip()
            content = str(payload.get("content") or "").strip()
            duration = int(payload.get("duration", 12000) or 12000)
            orient = Qt.Orientation.Vertical if len(content) > 120 or "\n" in content else Qt.Orientation.Horizontal

            factory = {
                "success": _InfoBar.success,
                "info": _InfoBar.info,
                "error": _InfoBar.error,
                "warning": _InfoBar.warning,
            }.get(level, _InfoBar.warning)

            bar = factory(
                title=title,
                content=content,
                orient=orient,
                isClosable=True,
                position=_IBPos.TOP_RIGHT,
                duration=duration,
                parent=self.host,
            )

            for button_info in payload.get("buttons") or []:
                button_text = str(button_info.get("text") or "").strip()
                callback = button_info.get("callback")
                if not button_text or not callable(callback) or bar is None:
                    continue

                btn = PushButton(button_text)
                btn.setAutoDefault(False)
                btn.setDefault(False)

                def _wrap(_checked=False, _btn=btn, _callback=callback):
                    try:
                        _btn.setEnabled(False)
                        _callback()
                    finally:
                        _btn.setEnabled(True)

                btn.clicked.connect(_wrap)
                bar.addWidget(btn)
        except Exception as e:
            log(f"Не удалось показать startup InfoBar: {e}", "DEBUG")

    def flush_startup_notification_queue(self) -> None:
        if not bool(getattr(self.host, "_startup_post_init_ready", False)):
            self.schedule_startup_notification_queue(300)
            return
        if not bool(getattr(self.host, "_startup_background_init_started", False)):
            self.schedule_startup_notification_queue(300)
            return
        if not self.host.isVisible():
            self.schedule_startup_notification_queue(500)
            return
        if not self._startup_notification_queue:
            return

        payload = self._startup_notification_queue.pop(0)
        self.show_startup_notification(payload)

        if self._startup_notification_queue:
            self.schedule_startup_notification_queue(900)

    def _add_autofix_button(self, bar, action: str) -> None:
        try:
            from qfluentwidgets import PushButton, InfoBar as _InfoBar, InfoBarPosition as _IBPos

            btn = PushButton("Исправить")
            btn.setFixedWidth(100)

            def on_fix():
                btn.setEnabled(False)
                btn.setText("...")
                try:
                    from dpi.process_health_check import execute_windivert_auto_fix

                    ok, msg = execute_windivert_auto_fix(action)
                    bar.close()
                    if ok:
                        _InfoBar.success(
                            title="Готово",
                            content=msg,
                            isClosable=True,
                            position=_IBPos.TOP,
                            duration=5000,
                            parent=self.host,
                        )
                    else:
                        _InfoBar.warning(
                            title="Не удалось",
                            content=msg,
                            isClosable=True,
                            position=_IBPos.TOP,
                            duration=8000,
                            parent=self.host,
                        )
                except Exception as e:
                    log(f"Auto-fix error: {e}", "ERROR")
                    btn.setEnabled(True)
                    btn.setText("Исправить")

            btn.clicked.connect(on_fix)
            bar.addWidget(btn)
        except Exception as e:
            log(f"Error adding auto-fix button: {e}", "DEBUG")

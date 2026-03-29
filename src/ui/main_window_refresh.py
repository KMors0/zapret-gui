from __future__ import annotations

from log import log
from ui.main_window_pages import get_loaded_page
from ui.page_names import PageName


def refresh_main_window_pages_after_preset_switch(window) -> None:
    """Refresh UI fragments that depend on the active preset."""
    try:
        page = get_loaded_page(window, PageName.ZAPRET2_DIRECT)
        if page and hasattr(page, "refresh_from_preset_switch"):
            page.refresh_from_preset_switch()
    except Exception as e:
        log(f"Ошибка обновления zapret2_strategies_page после смены пресета: {e}", "DEBUG")

    try:
        detail = get_loaded_page(window, PageName.ZAPRET2_STRATEGY_DETAIL)
        if detail and hasattr(detail, "refresh_from_preset_switch"):
            detail.refresh_from_preset_switch()
    except Exception as e:
        log(f"Ошибка обновления strategy_detail_page после смены пресета: {e}", "DEBUG")

    # Zapret 1 pages
    try:
        z1_page = get_loaded_page(window, PageName.ZAPRET1_DIRECT)
        if z1_page and hasattr(z1_page, "reload_for_mode_change"):
            z1_page.reload_for_mode_change()
    except Exception as e:
        log(f"Ошибка обновления zapret1_strategies_page после смены пресета: {e}", "DEBUG")

    try:
        z1_ctrl = get_loaded_page(window, PageName.ZAPRET1_DIRECT_CONTROL)
        if z1_ctrl and hasattr(z1_ctrl, "_refresh_preset_name"):
            z1_ctrl._refresh_preset_name()
    except Exception as e:
        log(f"Ошибка обновления zapret1_direct_control_page после смены пресета: {e}", "DEBUG")

    try:
        z2_ctrl = get_loaded_page(window, PageName.ZAPRET2_DIRECT_CONTROL)
        if z2_ctrl and hasattr(z2_ctrl, "_load_advanced_settings"):
            z2_ctrl._load_advanced_settings()
    except Exception as e:
        log(f"Ошибка обновления advanced toggles zapret2_direct_control_page после смены пресета: {e}", "DEBUG")

    try:
        orchestra_ctrl = get_loaded_page(window, PageName.ZAPRET2_ORCHESTRA_CONTROL)
        if orchestra_ctrl and hasattr(orchestra_ctrl, "_load_advanced_settings"):
            orchestra_ctrl._load_advanced_settings()
    except Exception as e:
        log(f"Ошибка обновления advanced toggles orchestra_zapret2_control_page после смены пресета: {e}", "DEBUG")

    try:
        display_name = window._get_direct_strategy_summary()
        if display_name:
            window.update_current_strategy_display(display_name)
    except Exception as e:
        log(f"Ошибка обновления display стратегии после смены пресета: {e}", "DEBUG")

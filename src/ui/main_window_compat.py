from __future__ import annotations

from ui.page_names import PageName
from ui.main_window_pages import get_loaded_page


def setup_main_window_compatibility_attrs(window) -> None:
    """Populate backward-compatibility attributes for legacy code paths."""
    method = ""
    try:
        from strategy_menu import get_strategy_launch_method

        method = (get_strategy_launch_method() or "").strip().lower()
    except Exception:
        method = ""

    current_strategy_label = None
    if method == "direct_zapret2_orchestra":
        orchestra_page = get_loaded_page(window, PageName.ZAPRET2_ORCHESTRA_CONTROL)
        if orchestra_page is not None and hasattr(orchestra_page, "strategy_label"):
            current_strategy_label = orchestra_page.strategy_label
    else:
        z2_control_page = get_loaded_page(window, PageName.ZAPRET2_DIRECT_CONTROL)
        if z2_control_page is not None and hasattr(z2_control_page, "strategy_label"):
            current_strategy_label = z2_control_page.strategy_label

    if current_strategy_label is None:
        control_page = get_loaded_page(window, PageName.CONTROL)
        if control_page is not None and hasattr(control_page, "strategy_label"):
            current_strategy_label = control_page.strategy_label

    if current_strategy_label is not None:
        window.current_strategy_label = current_strategy_label

    # Expose diagnostics sub-pages for backward-compat (cleanup, focus etc.)
    if PageName.BLOCKCHECK in window.pages:
        _blockcheck = window.pages[PageName.BLOCKCHECK]
        window.connection_page = getattr(_blockcheck, "connection_page", None)
        window.dns_check_page = getattr(_blockcheck, "dns_check_page", None)
    if PageName.HOSTS in window.pages:
        window.hosts_page = window.pages[PageName.HOSTS]

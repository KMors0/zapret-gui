from ui.nav_mode_config import get_nav_visibility
from ui.page_names import PageName


MODE_GATED_NAV_PAGES: frozenset[PageName] = frozenset({
    PageName.CONTROL,
    PageName.ZAPRET2_DIRECT_CONTROL,
    PageName.ZAPRET2_ORCHESTRA_CONTROL,
    PageName.ZAPRET1_DIRECT_CONTROL,
    PageName.ORCHESTRA,
    PageName.ORCHESTRA_SETTINGS,
})

MODE_SEARCH_PAGE_SCOPES: dict[str, frozenset[PageName]] = {
    "direct_zapret2": frozenset({
        PageName.ZAPRET2_DIRECT_CONTROL,
        PageName.ZAPRET2_DIRECT,
        PageName.ZAPRET2_USER_PRESETS,
        PageName.ZAPRET2_STRATEGY_DETAIL,
        PageName.ZAPRET2_PRESET_DETAIL,
    }),
    "direct_zapret2_orchestra": frozenset({
        PageName.ZAPRET2_ORCHESTRA_CONTROL,
        PageName.ZAPRET2_ORCHESTRA,
        PageName.ZAPRET2_ORCHESTRA_USER_PRESETS,
        PageName.ZAPRET2_ORCHESTRA_STRATEGY_DETAIL,
        PageName.ZAPRET2_PRESET_DETAIL,
    }),
    "direct_zapret1": frozenset({
        PageName.ZAPRET1_DIRECT_CONTROL,
        PageName.ZAPRET1_DIRECT,
        PageName.ZAPRET1_USER_PRESETS,
        PageName.ZAPRET1_STRATEGY_DETAIL,
        PageName.ZAPRET1_PRESET_DETAIL,
    }),
    "orchestra": frozenset({
        PageName.CONTROL,
        PageName.ORCHESTRA,
        PageName.ORCHESTRA_SETTINGS,
    }),
}

ALL_MODE_SEARCH_PAGES: frozenset[PageName] = frozenset().union(*MODE_SEARCH_PAGE_SCOPES.values())


def normalize_launch_method_for_ui(method: str | None) -> str:
    normalized = (method or "").strip().lower()
    return normalized or "direct_zapret2"


def should_add_nav_page_on_init(page_name: PageName, method: str | None) -> bool:
    normalized_method = normalize_launch_method_for_ui(method)
    if page_name not in MODE_GATED_NAV_PAGES:
        return True
    return bool(get_nav_visibility(normalized_method).get(page_name, False))


def get_sidebar_search_pages_for_method(method: str | None, all_pages: set[PageName]) -> set[PageName]:
    normalized_method = normalize_launch_method_for_ui(method)

    allowed_pages = set(all_pages)
    allowed_pages.difference_update(ALL_MODE_SEARCH_PAGES)
    allowed_pages.update(MODE_SEARCH_PAGE_SCOPES.get(normalized_method, frozenset()))
    return allowed_pages

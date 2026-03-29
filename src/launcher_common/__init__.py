"""Common utilities for Zapret launchers (V1 and V2).

This package intentionally uses lazy wrappers so legacy builder modules can
import submodules like ``launcher_common.blobs`` without triggering circular
imports through ``builder_factory`` / ``runner_factory`` at package import time.
"""

from .constants import *  # noqa: F401,F403


def get_strategy_runner(*args, **kwargs):
    from .runner_factory import get_strategy_runner as _impl
    return _impl(*args, **kwargs)


def reset_strategy_runner(*args, **kwargs):
    from .runner_factory import reset_strategy_runner as _impl
    return _impl(*args, **kwargs)


def invalidate_strategy_runner(*args, **kwargs):
    from .runner_factory import invalidate_strategy_runner as _impl
    return _impl(*args, **kwargs)


def get_current_runner(*args, **kwargs):
    from .runner_factory import get_current_runner as _impl
    return _impl(*args, **kwargs)


def combine_strategies(*args, **kwargs):
    from .builder_factory import combine_strategies as _impl
    return _impl(*args, **kwargs)


def calculate_required_filters(*args, **kwargs):
    from .builder_factory import calculate_required_filters as _impl
    return _impl(*args, **kwargs)


def get_strategy_display_name(*args, **kwargs):
    from .builder_factory import get_strategy_display_name as _impl
    return _impl(*args, **kwargs)


def get_active_targets_count(*args, **kwargs):
    from .builder_factory import get_active_targets_count as _impl
    return _impl(*args, **kwargs)


def validate_target_strategies(*args, **kwargs):
    from .builder_factory import validate_target_strategies as _impl
    return _impl(*args, **kwargs)


def apply_all_filters(*args, **kwargs):
    from .args_filters import apply_all_filters as _impl
    return _impl(*args, **kwargs)


def build_args_with_deduped_blobs(*args, **kwargs):
    from .blobs import build_args_with_deduped_blobs as _impl
    return _impl(*args, **kwargs)


def get_blobs_info(*args, **kwargs):
    from .blobs import get_blobs_info as _impl
    return _impl(*args, **kwargs)


def save_user_blob(*args, **kwargs):
    from .blobs import save_user_blob as _impl
    return _impl(*args, **kwargs)


def delete_user_blob(*args, **kwargs):
    from .blobs import delete_user_blob as _impl
    return _impl(*args, **kwargs)


def reload_blobs(*args, **kwargs):
    from .blobs import reload_blobs as _impl
    return _impl(*args, **kwargs)

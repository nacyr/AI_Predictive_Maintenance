import importlib


def safe_import(module_path: str, attr: str = None, default=None):
    """
    Safely import modules or attributes without crashing Streamlit.

    Example:
        predict = safe_import("ml.smart_engine", "predict_failure")
    """

    try:
        module = importlib.import_module(module_path)

        if attr:
            return getattr(module, attr, default)

        return module

    except Exception:
        return default
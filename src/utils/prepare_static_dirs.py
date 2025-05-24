from pathlib import Path


def prepare_static_dirs() -> Path:
    APP_ROOT = Path(__file__).resolve().parent.parent
    static_dir = APP_ROOT / "static"
    templates_dir = APP_ROOT / "templates"
    static_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    (templates_dir / "partials").mkdir(parents=True, exist_ok=True)
    return static_dir

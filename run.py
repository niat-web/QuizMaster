import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()


def is_debug_enabled() -> bool:
    """Return True only when FLASK_DEBUG is explicitly set to a truthy value."""
    return os.environ.get("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes"}


app = create_app()

if __name__ == "__main__":
    app.run(debug=is_debug_enabled())
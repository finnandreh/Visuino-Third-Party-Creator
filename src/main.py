"""
Entry point.

Keeps startup logic tiny so the rest of the code stays testable and reusable.
"""
from canvas_app import run_app


if __name__ == "__main__":
    # Delegates all GUI work to the module; easy to swap later.
    run_app()

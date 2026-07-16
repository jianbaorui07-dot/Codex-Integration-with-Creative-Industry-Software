from __future__ import annotations


def main() -> int:
    try:
        from .gui import run
    except ImportError:
        print(
            'VectorFlow Studio requires PySide6. Install it with: python -m pip install -e ".[vector-app]"'
        )
        return 1
    return run()


if __name__ == "__main__":
    raise SystemExit(main())

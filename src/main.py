# main.py
import argparse
from core.app import run_app

def main():
    parser = argparse.ArgumentParser(
        description="Juego Dino - Aprende matemáticas jugando."
    )
    parser.add_argument('--debug', action='store_true', help="Activa el modo debug")
    args = parser.parse_args()
    run_app(debug=args.debug)

if __name__ == "__main__":
    main()
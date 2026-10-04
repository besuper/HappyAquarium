import argparse
import logging

from . import create_app

def main():
    parser = argparse.ArgumentParser(prog="python -m happyaquarium", description="Happy Aquarium private server")
    parser.add_argument("--host", default="127.0.0.1", help="interface to bind (0.0.0.0 for LAN access)")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--debug", action="store_true", help="Flask debug mode (auto-reload)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    print(f"Happy Aquarium server: open http://{'localhost' if args.host in ('127.0.0.1', '0.0.0.0') else args.host}:{args.port}/")
    create_app().run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()

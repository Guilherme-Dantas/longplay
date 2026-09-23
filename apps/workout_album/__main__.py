from __future__ import annotations

import argparse
import json

from apps.workout_album.api import create_app
from apps.workout_album.run import RunRequest, user_message
from apps.workout_album.runtime import run_album_pick


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="longplay",
        description="Pick a Spotify album that matches a workout duration.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pick = sub.add_parser("pick", help="Run one recommendation")
    pick.add_argument("--duration", type=float, required=True, help="Session length in minutes")
    pick.add_argument("--criteria", required=True, help="What you want to hear")
    pick.add_argument("--tolerance", type=float, default=5.0, help="Allowed duration drift")

    serve = sub.add_parser("serve", help="HTTP API for the phone to call")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn

        uvicorn.run(create_app(), host=args.host, port=args.port)
        return

    req = RunRequest(
        duration_minutes=args.duration,
        criteria=args.criteria,
        tolerance_minutes=args.tolerance,
    )
    result = run_album_pick(user_message(req), stream=True)
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

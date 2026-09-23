from __future__ import annotations

from fastapi import FastAPI, HTTPException

from apps.workout_album.policy import AlbumPick
from apps.workout_album.run import RunRequest, user_message
from apps.workout_album.runtime import run_album_pick


def create_app() -> FastAPI:
    app = FastAPI(title="longplay", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/runs", response_model=AlbumPick)
    def runs(req: RunRequest) -> AlbumPick:
        try:
            return run_album_pick(user_message(req))
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return app


app = create_app()

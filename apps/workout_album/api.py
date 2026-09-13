from __future__ import annotations

from fastapi import FastAPI, HTTPException

from apps.workout_album.policy import AlbumPick, build_policy
from apps.workout_album.run import RunRequest, user_message
from apps.workout_album.tools import build_spotify_tools
from harness import AgentLoop


def build_loop() -> AgentLoop:
    return AgentLoop.from_env(tools=build_spotify_tools(), policy=build_policy())


def create_app() -> FastAPI:
    app = FastAPI(title="longplay", version="0.1.0")
    holder: dict[str, AgentLoop | None] = {"loop": None}

    def get_loop() -> AgentLoop:
        if holder["loop"] is None:
            holder["loop"] = build_loop()
        return holder["loop"]

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/runs", response_model=AlbumPick)
    def runs(req: RunRequest) -> AlbumPick:
        try:
            result = get_loop().run(user_message(req))
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        if not isinstance(result, AlbumPick):
            raise HTTPException(status_code=502, detail="unexpected harness output")
        return result

    return app


app = create_app()

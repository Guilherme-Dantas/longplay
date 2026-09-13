# Product

**longplay** picks one full album whose playing time matches a workout.

You say how long you will train and what you want to hear. The product returns a single catalog album — not a playlist, not a radio mix — that fits the clock and the taste.

The name is the pitch: a long-play record sized to the session.

## Who it is for

Someone about to train who would rather press play on a record than assemble a playlist. The session is the unit of time. The album is the unit of music.

## What a successful pick is

A pick is successful when all of these hold:

- There is exactly one album.
- Its runtime was measured from track lengths, not guessed.
- That runtime sits inside the session length plus a small tolerance.
- Among albums that already fit the clock, this one is the best match for the listening taste the user described.

If the clock and the taste fight, the clock wins. An album that overruns the session is not a pick, however perfect the genre.

## What it is not

- A DJ or a playlist generator. Tracks stay in album order.
- A Spotify clone. We search a catalog; we do not own the library.
- An on-device model. The phone (when it exists) asks our backend; the backend runs the agent.

## Current surface

- CLI: `python -m apps.workout_album pick`
- HTTP: `POST /runs` with session length, taste, and tolerance

User OAuth and the mobile client are later. Catalog search uses Spotify client credentials.

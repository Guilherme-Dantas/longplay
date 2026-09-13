# Spotify (for agents)

How longplay talks to Spotify. Read this before changing auth, the dashboard app, or catalog tools.

Official sources (re-check if Spotify changes the dashboard):

- [Authorization](https://developer.spotify.com/documentation/web-api/concepts/authorization)
- [Client credentials flow](https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow)
- [Redirect URIs](https://developer.spotify.com/documentation/web-api/concepts/redirect_uri)
- [Apps](https://developer.spotify.com/documentation/web-api/concepts/apps)
- [Getting started](https://developer.spotify.com/documentation/web-api/tutorials/getting-started)

Spotify is an **external catalog**, not a bounded context we own. See [bounded contexts](../domain/bounded-contexts.md). Domain words stay Session / album / runtime; Spotify ids are adapter details.

## Which OAuth flow we use

Spotify implements three grants. Pick by **who** is being authorized:

| Flow | User data (library, profile, playback) | Client secret on a server | Refresh token | longplay |
| --- | --- | --- | --- | --- |
| Client credentials | No | Yes | No (request a new access token) | **Now** — CLI / `POST /runs` backend |
| Authorization code | Yes | Yes | Yes | Later, if a **server** logs the user in |
| Authorization code + PKCE | Yes | No | Yes | Later, if the **phone** logs the user in |

Client credentials authenticates the **app**, not Guilherme's Spotify account. Search, album metadata, and track durations work. Saved albums, playlists, and “play this on my device” do **not**.

Do not add PKCE, redirect handlers, or scopes until someone asks for user resources. Do not put `SPOTIFY_CLIENT_SECRET` in a mobile app.

## Dashboard: create the app

1. [Developer Dashboard](https://developer.spotify.com/dashboard) → Create app.
2. Name / description can be `longplay`.
3. **Redirect URIs** is required on the form even though client credentials never redirects. Spotify’s own getting-started tutorial uses a dummy loopback URI for this reason.
4. Type `http://127.0.0.1:8000/callback` and click **Add**. The URI must appear as a chip, not only in the text box.
5. APIs: check **Web API** only. Not Web Playback SDK, iOS, or Android until we build those clients.
6. Accept Developer Terms → Create.
7. Settings → copy **Client ID** and **Client secret** (behind “View client secret”) into local `.env`:

```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

Never commit `.env`. Rotate the secret in the dashboard if it leaks.

### Redirect URI rules (enforced for new apps since 2025-04-09)

From Spotify’s redirect URI doc — this is why the dashboard rejected `example.org` / `localhost` in the text field:

- HTTPS required, **except** loopback, where HTTP is allowed.
- Loopback must be an IP literal: `http://127.0.0.1:PORT/callback` or `http://[::1]:PORT/callback`.
- **`localhost` is not allowed.**
- The registered URI must match the authorization request exactly (path, scheme, host). Exception: loopback may omit the port in the dashboard and add it at request time.
- Official examples: `https://example.com/callback`, `http://127.0.0.1:8000/callback`.

We register `http://127.0.0.1:8000/callback` to match our later `serve` port. The picker does not implement that callback yet.

New apps start in **Development Mode** (user and rate limits). Catalog search for a personal CLI is fine. A public mobile app will need a quota extension or extended mode.

## Token (what the code does)

Implementation: `apps/workout_album/spotify.py` → `SpotifyClient._access_token`.

```
POST https://accounts.spotify.com/api/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic base64(client_id:client_secret)

grant_type=client_credentials
```

`httpx` `auth=(id, secret)` is that Basic header. Spotify also documents sending `client_id` and `client_secret` in the body (getting-started curl); both are accepted. Prefer Basic, as in the [client credentials tutorial](https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow).

Response:

```json
{ "access_token": "...", "token_type": "Bearer", "expires_in": 3600 }
```

There is **no refresh_token** in this flow. Cache the access token until `expires_in` (we refresh ~30s early), then POST `/api/token` again.

Every Web API call:

```
Authorization: Bearer <access_token>
GET https://api.spotify.com/v1/...
```

Catalog tools we expose to the harness:

- `search_albums` — MusicBrainz discovery, then `GET /v1/search?type=album` by title/artist ([catalog.md](catalog.md)). Fallback: Spotify text search.
- `GET /v1/albums/{id}/tracks` → `get_album_tracks`
- `GET /v1/albums/{id}` + track sum → `get_album_duration`

Album runtime is summed in our domain (`sum_duration_ms`). Do not use a model guess and do not look for a duration field on the search payload — search albums do not include it.

## Agent checklist (do / don’t)

- **Do** keep secrets on the backend; the phone only calls `POST /runs`.
- **Do** fail with a clear error if `SPOTIFY_CLIENT_ID` / `SECRET` are empty (`SpotifyClient.configured()`).
- **Do** treat 401 as “fetch a new token”, 429 as rate limit (retry with backoff if we add it).
- **Don’t** implement user login “just in case.”
- **Don’t** copy Spotify playlist/playback types into Session Soundtrack language.
- **Don’t** tell the user to set Redirect URI to `localhost` or to skip Add on the dashboard.

When user OAuth is actually requested (save-to-library, or **listening history** so we stop repeating albums they already know — see [product later](../product-later.md)): Authorization Code + PKCE on the phone (secret must not live on the device), new redirect URI still `127.0.0.1` or an `https` app URL, and scopes chosen from the [scopes list](https://developer.spotify.com/documentation/web-api/concepts/scopes). Until then, this file is the whole contract.

# longplay

Um disco no tamanho da sessão. O repo tem um **harness** próprio (OpenAI-compatible) e, em cima dele, um picker de álbum do Spotify pela duração do treino.

O harness é código deste projeto e vai para o GitHub. Ollama, chaves e pesos de modelo ficam na sua máquina — runtime, não o repositório.

## Peças

- `harness/` — `ModelClient`, `ToolRegistry`, `Policy`, `AgentLoop`
- `examples/hello.py` — tool fake (`get_time`) para provar o loop
- `apps/workout_album/` — tools Spotify + policy + CLI/`POST /runs`

O celular não chama o modelo. Chama o backend (`POST /runs`). Duração de álbum vem da soma de `duration_ms` das faixas, nunca da cabeça do LLM.

## Setup

```powershell
cd F:\homelab\longplay
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
```

Edite `.env`:

| Variável | Local (Ollama) | Nuvem (OpenRouter) |
| --- | --- | --- |
| `MODEL_BASE_URL` | `http://localhost:11434/v1` | `https://openrouter.ai/api/v1` |
| `MODEL_API_KEY` | `ollama` | sua chave |
| `MODEL_NAME` | `qwen3:8b` | slug do modelo (`openrouter/free`, `deepseek/deepseek-chat`, etc.) |

Fallback: se o local cair, o loop tenta `FALLBACK_*`. Sem `if` de vendor no código — os dois lados falam o mesmo `chat.completions`.

Spotify (client credentials, sem OAuth de usuário):

1. App em [developer.spotify.com](https://developer.spotify.com/dashboard)
2. `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` no `.env`

## Hello harness

```powershell
python examples/hello.py
```

## Picker de álbum

```powershell
python -m apps.workout_album pick --duration 45 --criteria "eletronico instrumental"
python -m apps.workout_album serve
```

`POST /runs`:

```json
{
  "duration_minutes": 45,
  "criteria": "eletronico, sem vocal",
  "tolerance_minutes": 5
}
```

## Ollama (opcional)

Na RTX 3060, 8B é o daily driver:

```powershell
winget install Ollama.Ollama
ollama pull qwen3:8b
```

Quem clona sem GPU aponta `MODEL_*` para o OpenRouter e roda igual.

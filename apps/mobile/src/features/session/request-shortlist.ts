import type { AlbumFit, Shortlist } from "@/features/session/types";

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

type AlbumPickJson = {
  album_id: string;
  name: string;
  artists: string[];
  duration_minutes: number;
  reason: string;
  spotify_url: string;
  year?: number;
  image_url?: string | null;
};

export class PickError extends Error {}

export async function requestShortlist(
  input: { durationMinutes: number; criteria: string },
  signal: AbortSignal,
): Promise<Shortlist> {
  const response = await fetch(`${API_URL}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      duration_minutes: input.durationMinutes,
      criteria: input.criteria,
      tolerance_minutes: 5,
    }),
    signal,
  });

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const detail =
      isRecord(body) && typeof body.detail === "string" ? body.detail : "The picker did not answer.";
    throw new PickError(detail);
  }
  if (!isPick(body)) throw new PickError("The picker did not answer.");
  return { recommendation: toFit(body, "recommendation"), fits: [] };
}

function toFit(pick: AlbumPickJson, role: AlbumFit["role"]): AlbumFit {
  return {
    albumId: pick.album_id,
    name: pick.name,
    artists: pick.artists.filter((artist) => typeof artist === "string"),
    durationMinutes: pick.duration_minutes,
    reason: pick.reason,
    spotifyUrl: pick.spotify_url,
    role,
    year: typeof pick.year === "number" ? pick.year : undefined,
    imageUrl: spotifyCoverUrl(pick.image_url),
  };
}

function spotifyCoverUrl(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  try {
    const url = new URL(value);
    const host = url.hostname.toLowerCase();
    if (url.protocol !== "https:") return undefined;
    if (host !== "i.scdn.co" && !host.endsWith(".scdn.co")) return undefined;
    return url.toString();
  } catch {
    return undefined;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isPick(value: unknown): value is AlbumPickJson {
  if (!isRecord(value)) return false;
  return (
    typeof value.album_id === "string" &&
    typeof value.name === "string" &&
    Array.isArray(value.artists) &&
    typeof value.duration_minutes === "number" &&
    typeof value.reason === "string" &&
    typeof value.spotify_url === "string"
  );
}

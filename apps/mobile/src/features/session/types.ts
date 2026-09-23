export type AlbumRole = "recommendation" | "fit";

/** One album that fits the clock. `year` arrives when the API starts sending it. */
export type AlbumFit = {
  albumId: string;
  name: string;
  artists: string[];
  durationMinutes: number;
  reason: string;
  spotifyUrl: string;
  role: AlbumRole;
  year?: number;
  /** Spotify cover. Absent when the album has no image; the disc keeps its color. */
  imageUrl?: string;
};

/**
 * The phone's result. Today `POST /runs` returns one recommendation and `fits` is empty.
 * When the API grows a shortlist, fill `fits` here (up to four) and the reel already renders them.
 */
export type Shortlist = {
  recommendation: AlbumFit;
  fits: AlbumFit[];
};

export function shortlistAlbums(shortlist: Shortlist): AlbumFit[] {
  return [shortlist.recommendation, ...shortlist.fits];
}

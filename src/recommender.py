import csv
import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# ── constants ────────────────────────────────────────────────────────────────
TEMPO_MAX = 200.0    # BPM ceiling; used to normalize tempo onto [0, 1]
DEFAULT_SIGMA = 0.20 # Gaussian pickiness (0.20 is more forgiving than 0.15)

# ── helpers ──────────────────────────────────────────────────────────────────

def gaussian(x: float, mu: float, sigma: float) -> float:
    """Gaussian (RBF) kernel: returns 1.0 for a perfect match, ~0.0 far away."""
    return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))


def _default_weights() -> Dict[str, float]:
    """Return the default feature weights used when none are supplied in the profile."""
    # weights sum to 1.00
    return {
        "energy":       0.30,  # most audibly noticeable feature
        "genre":        0.20,  # categorical: preferred genre list
        "acousticness": 0.20,  # organic vs. electronic texture
        "mood":         0.15,  # categorical: preferred mood list (raised)
        "tempo":        0.10,  # rhythmic consistency (normalized BPM)
        "valence":      0.05,  # musical positivity / brightness
    }

# ── data classes ─────────────────────────────────────────────────────────────

@dataclass
class Song:
    """Represents a single song and its audio attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genres: List[str]       # multi-genre list
    favorite_moods: List[str]        # multi-mood list (now carries 0.15 weight)
    target_energy: float             # 0–1
    target_tempo: float              # BPM — normalized to 0–1 internally
    target_acousticness: float       # 0–1
    target_valence: float            # 0–1
    sigma: float = DEFAULT_SIGMA
    weights: Dict[str, float] = field(default_factory=_default_weights)

# ── core scoring ─────────────────────────────────────────────────────────────

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score one song against a dict-based user profile using a point system.

    Point budget (max 10.0 pts):
        genre match          +2.0  (binary: song genre in favorite_genres)
        mood match           +1.5  (binary: song mood in favorite_moods)
        energy proximity     +3.0  (Gaussian × 3.0 — most audibly noticeable)
        acousticness prox.   +2.0  (Gaussian × 2.0 — organic vs. electronic)
        tempo proximity      +1.0  (Gaussian × 1.0 — normalized BPM)
        valence proximity    +0.5  (Gaussian × 0.5 — musical brightness)

    Returns
    -------
    (score, reasons)
        score   – total points accumulated (0.0 – 10.0)
        reasons – one string per feature showing its point contribution,
                  e.g. "genre match (+2.00)", "energy proximity (+2.85)"
    """
    sigma = user_prefs.get("sigma", DEFAULT_SIGMA)

    score = 0.0
    reasons: List[str] = []

    # ── categorical: genre match (+2.0) ──────────────────────────────────────
    if song["genre"] in user_prefs.get("favorite_genres", []):
        pts = 2.0
        score += pts
        reasons.append(f"genre match (+{pts:.2f})")

    # ── categorical: mood match (+1.5) ───────────────────────────────────────
    if song["mood"] in user_prefs.get("favorite_moods", []):
        pts = 1.5
        score += pts
        reasons.append(f"mood match (+{pts:.2f})")

    # ── numeric: energy proximity (Gaussian × 3.0, max +3.0) ────────────────
    energy_pts = gaussian(
        song["energy"],
        user_prefs.get("target_energy", 0.5),
        sigma,
    ) * 3.0
    score += energy_pts
    reasons.append(
        f"energy proximity (+{energy_pts:.2f})  "
        f"[song={song['energy']:.2f}  target={user_prefs.get('target_energy', 0.5):.2f}]"
    )

    # ── numeric: acousticness proximity (Gaussian × 2.0, max +2.0) ──────────
    acousticness_pts = gaussian(
        song["acousticness"],
        user_prefs.get("target_acousticness", 0.5),
        sigma,
    ) * 2.0
    score += acousticness_pts
    reasons.append(
        f"acousticness proximity (+{acousticness_pts:.2f})  "
        f"[song={song['acousticness']:.2f}  target={user_prefs.get('target_acousticness', 0.5):.2f}]"
    )

    # ── numeric: tempo proximity (Gaussian × 1.0, max +1.0) ─────────────────
    # BPM is normalized to [0, 1] before Gaussian — a shared sigma of 0.20
    # would reject any song differing by even 1 BPM without normalization.
    tempo_pts = gaussian(
        song["tempo_bpm"] / TEMPO_MAX,
        user_prefs.get("target_tempo", 100) / TEMPO_MAX,
        sigma,
    ) * 1.0
    score += tempo_pts
    reasons.append(
        f"tempo proximity (+{tempo_pts:.2f})  "
        f"[song={int(song['tempo_bpm'])} BPM  target={int(user_prefs.get('target_tempo', 100))} BPM]"
    )

    # ── numeric: valence proximity (Gaussian × 0.5, max +0.5) ───────────────
    valence_pts = gaussian(
        song["valence"],
        user_prefs.get("target_valence", 0.5),
        sigma,
    ) * 0.5
    score += valence_pts
    reasons.append(
        f"valence proximity (+{valence_pts:.2f})  "
        f"[song={song['valence']:.2f}  target={user_prefs.get('target_valence', 0.5):.2f}]"
    )

    return score, reasons

# ── I/O ──────────────────────────────────────────────────────────────────────

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file and return a list of typed dicts."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

# ── functional API ────────────────────────────────────────────────────────────

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song, sort by score descending, return the top-k.

    Uses a list comprehension to build all (song, score, explanation) tuples
    in one pass, then sorted() to produce a new ranked list without mutating
    the original catalog.  sorted() is preferred over .sort() here because
    recommend_songs() should be a pure function — calling it twice on the same
    catalog must give the same result, which .sort() (in-place mutation) would
    violate if the caller reuses the scored list.

    Returns
    -------
    List of (song_dict, score, explanation_string) ordered highest → lowest.
    """
    # ── score every song in one readable pass ────────────────────────────────
    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in (score_song(user_prefs, song),)
    ]

    # ── sorted() returns a NEW list ranked highest → lowest ──────────────────
    # key=lambda x: x[1]  →  sort by the score (index 1 of each tuple)
    # reverse=True         →  highest score first
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]

# ── OOP API (used by tests) ───────────────────────────────────────────────────

class Recommender:
    """Object-oriented wrapper around the functional scoring pipeline."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _profile_to_dict(self, user: UserProfile) -> Dict:
        """Convert a UserProfile dataclass into the dict format expected by score_song."""
        return {
            "favorite_genres":     user.favorite_genres,
            "favorite_moods":      user.favorite_moods,
            "target_energy":       user.target_energy,
            "target_tempo":        user.target_tempo,
            "target_acousticness": user.target_acousticness,
            "target_valence":      user.target_valence,
            "sigma":               user.sigma,
            "weights":             user.weights,
        }

    def _song_to_dict(self, song: Song) -> Dict:
        """Convert a Song dataclass into the dict format expected by score_song."""
        return {
            "id":           song.id,
            "title":        song.title,
            "artist":       song.artist,
            "genre":        song.genre,
            "mood":         song.mood,
            "energy":       song.energy,
            "tempo_bpm":    song.tempo_bpm,
            "valence":      song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for this user."""
        user_dict = self._profile_to_dict(user)
        scored = [
            (song, score_song(user_dict, self._song_to_dict(song))[0])
            for song in self.songs
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why this song was recommended."""
        _, reasons = score_song(self._profile_to_dict(user), self._song_to_dict(song))
        if not reasons:
            return (
                f"'{song.title}' is a partial match based on its audio profile "
                f"(energy {song.energy:.2f}, acousticness {song.acousticness:.2f}, "
                f"{song.tempo_bpm:.0f} BPM)."
            )
        return f"'{song.title}' was recommended because: {'; '.join(reasons)}."

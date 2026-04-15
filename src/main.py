"""
Command line runner for the Music Recommender Simulation.
Run from the project root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs

# ── display helpers ───────────────────────────────────────────────────────────

WIDTH = 64

def divider(char: str = "-") -> None:
    print(char * WIDTH)

def header(text: str) -> None:
    divider("=")
    print(f"  {text}")
    divider("=")

def print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    """Print one ranked result in a structured block."""
    divider()
    print(f"  #{rank}  {song['title']}  -  {song['artist']}")
    print(f"       Genre: {song['genre']}   Mood: {song['mood']}")
    print(f"       Score: {score:.2f} / 12.00")
    divider(".")
    print("  Why this song:")
    for reason in explanation.split("; "):
        print(f"    * {reason.strip()}")

def run_profile(label: str, note: str, profile: dict, songs: list, k: int = 5) -> None:
    """Score the catalog against one profile and print the full ranked block."""
    recs = recommend_songs(profile, songs, k=k)
    header(label)
    print(f"  Note   : {note}")
    print(f"  Genres : {profile['favorite_genres']}")
    print(f"  Moods  : {profile['favorite_moods']}")
    print(f"  Energy target : {profile['target_energy']}   "
          f"Tempo target : {profile['target_tempo']} BPM")
    print()
    for rank, (song, score, explanation) in enumerate(recs, start=1):
        print_recommendation(rank, song, score, explanation)
    divider("=")
    print()

# ── profiles ─────────────────────────────────────────────────────────────────

# 1. Standard — High-Energy Pop
HIGH_ENERGY_POP = {
    "favorite_genres":     ["pop", "indie pop", "synthwave"],
    "favorite_moods":      ["happy", "intense", "moody"],
    "target_energy":       0.82,
    "target_tempo":        124,
    "target_acousticness": 0.18,
    "target_valence":      0.82,
    "sigma":               0.20,
}

# 2. Standard — Chill Lofi Study Session
CHILL_LOFI = {
    "favorite_genres":     ["lofi", "ambient", "jazz"],
    "favorite_moods":      ["chill", "focused", "relaxed"],
    "target_energy":       0.38,
    "target_tempo":        80,
    "target_acousticness": 0.80,
    "target_valence":      0.60,
    "sigma":               0.20,
}

# 3. Standard — Deep Intense Rock
DEEP_ROCK = {
    "favorite_genres":     ["rock", "metal", "synthwave"],
    "favorite_moods":      ["intense", "angry", "moody"],
    "target_energy":       0.93,
    "target_tempo":        160,
    "target_acousticness": 0.08,
    "target_valence":      0.35,
    "sigma":               0.20,
}

# 4. Edge case — The Contradiction
#    Numeric targets scream "high-energy club banger" (energy 0.95, fast tempo,
#    zero acousticness) but categorical preferences say "sad soul ballad."
#    Expected surprise: soul/sad songs may still rank low despite mood match
#    because their numeric features are completely opposite.
CONTRADICTION = {
    "favorite_genres":     ["soul", "classical"],
    "favorite_moods":      ["sad", "melancholic"],
    "target_energy":       0.95,
    "target_tempo":        150,
    "target_acousticness": 0.05,
    "target_valence":      0.20,
    "sigma":               0.20,
}

# 5. Edge case — The Invisible User
#    All numeric targets sit exactly at the midpoint (0.5 / 100 BPM).
#    No genre or mood preferences at all.
#    Expected surprise: the system can only use numeric proximity, so mid-range
#    songs float up regardless of whether they "feel" related.
INVISIBLE_USER = {
    "favorite_genres":     [],
    "favorite_moods":      [],
    "target_energy":       0.50,
    "target_tempo":        100,
    "target_acousticness": 0.50,
    "target_valence":      0.50,
    "sigma":               0.20,
}

# 6. Edge case — Genre Ghost
#    Favorite genres that do not exist anywhere in the catalog
#    (country, k-pop, reggae).  Every song scores 0 on genre (+2.0 points lost).
#    Expected surprise: ranking falls back entirely on numeric proximity,
#    potentially surfacing unexpected songs at the top.
GENRE_GHOST = {
    "favorite_genres":     ["country", "k-pop", "reggae"],
    "favorite_moods":      ["happy", "euphoric"],
    "target_energy":       0.75,
    "target_tempo":        110,
    "target_acousticness": 0.30,
    "target_valence":      0.85,
    "sigma":               0.20,
}

# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    run_profile(
        "Profile 1 - High-Energy Pop",
        "Standard upbeat listener: pop/indie pop, happy and intense",
        HIGH_ENERGY_POP, songs,
    )
    run_profile(
        "Profile 2 - Chill Lofi Study Session",
        "Standard study listener: lofi/ambient/jazz, chill and focused",
        CHILL_LOFI, songs,
    )
    run_profile(
        "Profile 3 - Deep Intense Rock",
        "Standard rock listener: rock/metal, intense and angry",
        DEEP_ROCK, songs,
    )
    run_profile(
        "Profile 4 [EDGE] - The Contradiction",
        "SAD genres/moods but HIGH-ENERGY numeric targets — can the scorer be tricked?",
        CONTRADICTION, songs,
    )
    run_profile(
        "Profile 5 [EDGE] - The Invisible User",
        "No genre/mood preferences, all numeric targets at midpoint (0.5 / 100 BPM)",
        INVISIBLE_USER, songs,
    )
    run_profile(
        "Profile 6 [EDGE] - Genre Ghost",
        "Favorite genres (country, k-pop, reggae) don't exist in catalog — zero genre points",
        GENRE_GHOST, songs,
    )


if __name__ == "__main__":
    main()

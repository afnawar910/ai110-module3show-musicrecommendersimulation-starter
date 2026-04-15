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
    print(f"       Score: {score:.2f} / 10.00")
    divider(".")
    print("  Why this song:")
    for reason in explanation.split("; "):
        print(f"    * {reason.strip()}")

# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    songs = load_songs("data/songs.csv")

    # ── user profile: pop / happy ─────────────────────────────────────────────
    taste_profile = {
        "favorite_genres":     ["pop", "indie pop", "synthwave"],
        "favorite_moods":      ["happy", "intense", "moody"],
        "target_energy":       0.80,
        "target_tempo":        120,
        "target_acousticness": 0.20,
        "target_valence":      0.80,
        "sigma":               0.20,
    }

    recommendations = recommend_songs(taste_profile, songs, k=5)

    header("Music Recommender Simulation")
    print(f"  Catalog size : {len(songs)} songs")
    print(f"  Profile      : pop / happy / high-energy")
    print(f"  Returning    : top {len(recommendations)} results")

    print()
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation)

    divider("=")
    print()


if __name__ == "__main__":
    main()

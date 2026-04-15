from src.recommender import Song, UserProfile, Recommender


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1, title="Test Pop Track", artist="Test Artist",
            genre="pop", mood="happy",
            energy=0.8, tempo_bpm=120, valence=0.9,
            danceability=0.8, acousticness=0.2,
        ),
        Song(
            id=2, title="Chill Lofi Loop", artist="Test Artist",
            genre="lofi", mood="chill",
            energy=0.4, tempo_bpm=80, valence=0.6,
            danceability=0.5, acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genres=["pop"],
        favorite_moods=["happy"],
        target_energy=0.8,
        target_tempo=120,
        target_acousticness=0.2,
        target_valence=0.9,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # pop/happy song should outscore lofi/chill for this profile
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genres=["pop"],
        favorite_moods=["happy"],
        target_energy=0.8,
        target_tempo=120,
        target_acousticness=0.2,
        target_valence=0.9,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_mood_match_raises_score():
    """A song whose mood matches the profile should score higher than one that doesn't."""
    user = UserProfile(
        favorite_genres=[],
        favorite_moods=["chill"],
        target_energy=0.5,
        target_tempo=100,
        target_acousticness=0.5,
        target_valence=0.5,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    # lofi/chill song should rank first because mood matches (weight 0.15)
    assert results[0].mood == "chill"

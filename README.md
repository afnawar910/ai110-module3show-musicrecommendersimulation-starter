# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

This project is a working CLI-first music recommender simulation. Running `python -m src.main` loads an 18-song catalog from `data/songs.csv`, scores every song against a user taste profile using a Gaussian proximity algorithm, and prints a clean ranked list of the top 5 results with point-by-point explanations directly in the terminal. Each song is scored out of 10 points across six features — genre match (+2.0), mood match (+1.5), energy proximity (up to +3.0), acousticness proximity (up to +2.0), tempo proximity (up to +1.0), and valence proximity (up to +0.5) — so every recommendation comes with a transparent, human-readable reason for why it was chosen.

---

## How The System Works

### How Real-World Recommenders Work — and What This Version Prioritizes

Real-world systems like Spotify and YouTube operate as multi-stage pipelines. In Stage 1 (Candidate Generation), approximate nearest-neighbor algorithms narrow a library of millions of songs down to a few hundred candidates in milliseconds by grouping songs into similarity neighborhoods. In Stage 2 (Scoring), each candidate receives a relevance score computed from the user's taste profile — often using Gaussian proximity across many audio dimensions simultaneously. In Stage 3 (Ranking), business logic is layered on top: diversity rules prevent the same artist from dominating the list, freshness bonuses surface new releases, and contextual signals (time of day, activity) shift feature weights in real time. This simulation focuses on **Stage 2** — the scoring engine — using a Gaussian (RBF) kernel to reward songs that land exactly on a user's preferred energy, tempo, and acousticness values, combined with binary categorical matching on mood and genre. The ranking stage is kept simple (top-N by score) so the scoring logic stays transparent and easy to inspect.

---
![alt text](image.png)

### Song Features

Each `Song` object stores the following attributes drawn directly from `songs.csv`:

| Feature | Type | Role in scoring |
|---|---|---|
| `genre` | string | Binary match against `favorite_genres` list (weight **0.20**) |
| `mood` | string | Binary match against `favorite_moods` list (weight **0.15**) |
| `energy` | float 0–1 | Gaussian proximity to `target_energy` (weight **0.30**) |
| `acousticness` | float 0–1 | Gaussian proximity to `target_acousticness` (weight **0.20**) |
| `tempo_bpm` | integer | Gaussian proximity to `target_tempo` after ÷200 normalization (weight **0.10**) |
| `valence` | float 0–1 | Gaussian proximity to `target_valence` (weight **0.05**) |
| `danceability` | float 0–1 | Loaded but not scored — reserved for future experiments |

### UserProfile Features

Each `UserProfile` object stores:

| Field | Type | Purpose |
|---|---|---|
| `favorite_genres` | list of strings | Genres the user prefers; binary 1.0 match, else 0.0 |
| `favorite_moods` | list of strings | Moods the user prefers; binary 1.0 match, else 0.0 |
| `target_energy` | float 0–1 | Center (μ) of the Gaussian for energy |
| `target_tempo` | float BPM | Center (μ) for tempo; normalized to 0–1 before scoring |
| `target_acousticness` | float 0–1 | Center (μ) of the Gaussian for acousticness |
| `target_valence` | float 0–1 | Center (μ) of the Gaussian for valence |
| `sigma` | float | Gaussian pickiness — default **0.20** (more forgiving than 0.15) |
| `weights` | dict | Per-feature weights; must sum to 1.0 |

---

### Algorithm Recipe (Finalized)

**Step 1 — Load catalog**
Parse `data/songs.csv` into a list of typed song dicts using `load_songs()`.

**Step 2 — For each song, call `score_song(user_prefs, song)`**

Compute six sub-scores:

```
energy_score       = gaussian(song.energy,            target_energy,            σ)
acousticness_score = gaussian(song.acousticness,       target_acousticness,      σ)
valence_score      = gaussian(song.valence,            target_valence,           σ)
tempo_score        = gaussian(song.tempo_bpm / 200,    target_tempo / 200,       σ)

genre_score        = 1.0  if song.genre in favorite_genres  else 0.0
mood_score         = 1.0  if song.mood  in favorite_moods   else 0.0
```

where `gaussian(x, μ, σ) = e ^ ( -(x − μ)² / (2σ²) )`

**Step 3 — Weighted sum**

```
total = 0.30 × energy_score
      + 0.20 × genre_score
      + 0.20 × acousticness_score
      + 0.15 × mood_score
      + 0.10 × tempo_score
      + 0.05 × valence_score
```

**Step 4 — Rank and return**
Collect `(song, total, explanation)` for all songs, sort descending by `total`, return top-k.

---

### Potential Biases to Watch For

- **Genre + acousticness dominance** — Together genre (0.20) and acousticness (0.20) account for 40% of the score. A song in the wrong genre but with a perfect acoustic texture will still outscore a genre-matched song with slightly wrong acousticness. This could surface folk or classical songs for a lofi user when the catalog expands.
- **Mood under-reward before the fix, over-reward risk now** — Raising mood from 0.05 → 0.15 means a song with a matching mood but mismatched energy (e.g., an *intense* lofi track) could still rank highly. Monitor whether mood match is pulling the wrong songs up.
- **Binary categorical cliff** — Genre and mood are all-or-nothing (1.0 or 0.0). A song with a closely related genre (e.g., `indie pop` vs `pop`) scores zero on genre regardless of how similar it actually sounds.
- **Small catalog amplifies outliers** — With only 18 songs, a single weight change visibly reshapes the entire top-5. Results will stabilize with a larger catalog.
- **No diversity enforcement** — If multiple songs share the same top-scoring genre and mood, they will all cluster at the top with no mechanism to surface variety.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"


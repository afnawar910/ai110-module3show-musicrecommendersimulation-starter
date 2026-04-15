# Model Card: Music Recommender Simulation

## 1. Model Name

**RESONATE 1.0**

A rule-based music recommender that scores songs against a user taste profile and returns the top 5 matches.

## 2. Goal / Task

RESONATE 1.0 suggests songs that fit a user's taste. It looks at what genres, moods, energy level, and sound texture a user likes. It scores every song in the catalog and returns the 5 best matches. It is built for a classroom project, not a real app.

## 3. Data Used

The catalog is the file `data/songs.csv`. It has **18 songs**. Each song has a genre, mood, energy (a number from 0 to 1), tempo in BPM, how acoustic it sounds, how bright or positive it feels (valence), and how danceable it is. Danceability is stored but not used in scoring yet.

Genres in the catalog include pop, lofi, rock, metal, jazz, ambient, classical, hip-hop, indie pop, r&b, folk, latin, soul, synthwave, and edm. Moods include happy, chill, intense, sad, melancholic, euphoric, focused, relaxed, angry, moody, nostalgic, romantic, and confident.

Limits of the data: 18 songs is very small. There is no country, k-pop, or reggae. The catalog leans toward Western pop and electronic music. A user who likes other styles will get poor results.

## 4. Algorithm Summary

Every song gets a score out of 12 points. The points come from six things.

Genre match gives up to 1 point. If the song's genre is in the user's favorites list, it gets the full point. If not, it gets zero.

Mood match gives up to 1.5 points. Same idea: match earns points, no match earns nothing.

Energy proximity gives up to 6 points. The closer the song's energy is to the user's target, the more points it earns. This uses a bell curve shape so songs that are "close enough" still score well.

Acousticness proximity gives up to 2 points. It works the same way as energy but for how organic or electronic the song sounds.

Tempo proximity gives up to 1 point. It compares the song's BPM to the user's target tempo.

Valence proximity gives up to 0.5 points. It compares how bright or positive the song feels against the user's preference.

After all 18 songs are scored, they are sorted from highest to lowest. The top 5 are returned with a plain-English breakdown showing how each point was earned.

## 5. Observed Behavior / Biases

The biggest pattern discovered is that energy dominates everything else. Energy is worth up to 6 out of 12 points. That is half the total score. This means a song with the right energy can beat songs that match the user's genre and mood but have slightly different energy.

This caused a real problem in testing. A user who asked for sad, quiet classical music still got Iron Tempest (a loud metal song) as the top result. The reason was that Iron Tempest's energy matched the user's numeric target. The system never noticed that the words "sad" and "classical" and the number 0.95 energy were contradicting each other.

Another pattern: if a user's favorite genres do not exist in the catalog, the system does not warn them. It just ignores the genre preference silently and scores based on everything else.

## 6. Evaluation Process

Six user profiles were tested. Three were normal listener types: a high-energy pop fan, a chill lofi study listener, and a deep intense rock fan. Three were edge cases designed to break the system: The Contradiction (sad genres but high-energy targets), The Invisible User (no preferences at all), and The Genre Ghost (genres that do not exist in the catalog).

The three normal profiles all gave good results. The right songs came up first, scores felt reasonable, and the explanations made sense.

The edge cases revealed real weaknesses. The Contradiction profile got loud metal songs even though the user asked for quiet, sad music. The Invisible User got an R&B ballad as the top pick with no explanation for why. The Genre Ghost got no warning that none of its favorite genres existed.

Automated tests in `tests/test_recommender.py` also checked that scores stayed within the 0 to 12 range and that the ranking order was correct.

## 7. Intended Use and Non-Intended Use

**Intended use:** Classroom exploration of how scoring and ranking work in recommender systems. It is meant to be read, tested, and experimented with by students learning about AI.

**Not intended for:** Real users picking music to listen to. Not intended for large catalogs. Not intended for users whose taste does not fit neatly into a numeric profile. Not intended for any production or commercial purpose.

## 8. Ideas for Improvement

First, add a warning when the user's words and numbers conflict. If someone lists "classical" and "sad" as favorites but sets a very high energy target, the system should tell them before returning results. Something like "your genre preferences suggest quiet music but your energy target is very high" would help a lot.

Second, replace the all-or-nothing genre matching with soft similarity. Right now "lofi" and "ambient" share zero overlap even though they sound similar. A simple table of related genres would give partial credit for near-matches and fix the Genre Ghost problem.

Third, let the energy weight adjust based on context. When the user has strong genre and mood preferences, lower the energy weight so those preferences can actually influence the result. Right now energy at 50 percent of the score is too powerful to be overridden by anything else.

## 9. Personal Reflection

My biggest learning moment was running the Contradiction profile and watching the system recommend Iron Tempest to a user who asked for sad, quiet music. That was the moment it became real to me. The system is not listening. It is doing math. The word "sad" and the number 0.95 energy never interacted with each other at all. Seeing that made me understand why real recommenders sometimes feel frustratingly off.

AI tools helped me work through the Gaussian formula quickly and understand why normalizing tempo to a 0 to 1 scale mattered. But I could not just trust the tool's explanations. I had to go back and trace the actual point totals myself to make sure they matched. The tool was useful for explaining ideas but it was not a substitute for checking the numbers.

What surprised me most was how good the normal profiles felt. High-Energy Pop and Chill Lofi returned exactly what I would expect from a human DJ. That was shocking because the algorithm has no idea what music sounds like. It only knows that 0.82 is close to 0.82. The good feeling came from the data being well-labeled, not from the algorithm being smart. That changed how I think about Spotify and similar apps. The magic is in the data, not the math.

If I kept developing this I would add a thumbs-up and thumbs-down button after each recommendation. Those clicks would shift the user's energy and acousticness targets over time automatically. That one change would turn a static scorer into something that actually learns, which is how real taste profiles work.

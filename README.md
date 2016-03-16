# NCAA Men's Basketball Ratings for 2016

This is a last-minute thing I put together to try to rate teams using the Elo rating system so I can fill out my bracket.

## Source data
The source data I used is from [Massey Ratings](http://www.masseyratings.com/scores.php?s=284067&sub=284067&all=1) and [Spreadsheet Sports](https://www.spreadsheet-sports.com/2015-ncaa-basketball-game-data). No effort was made to do any checking/scrubbing of the data, as it was assumed that the source data was clean enough.

### Data Format for Massey Ratings

CSV file with the following fields:
- days since 1-1-0000
- YYYYMMDD
- team1 index (zero if a non-conference team)
- homefield1 (1=home, -1=away, 0=neutral)
- score1
- team2 index (zero if a non-conference team)
- homefield2 (1=home, -1=away, 0=neutral)
- score2

## Methodology
The methodology used is based off of the Elo rating system.

### Initial computation of ratings
The initial rating of each team was set to 1000. Each game throughout the season was then processed sequentially by order of date. To update the rating of the two teams, the following code was used:

```python
K = 30

# Expected win probability for team 1
expected_win_prob_team1 = 1.0/(1 + 10**((rating2 - rating1)/400))

# Compute bonus based on score differential
bonus = 1.0*abs(score1 - score2)/(score1 + score2)

change = K * (1 + bonus) * expected_win_prob_team1
```

### Adjusting for Strength of Schedule
First the average rating of each of the opponents played for a team was computed. An adjusted rating was computed as follows:

```python
adjusted_rating = original_rating * (average_opponent_rating/1000)**1.5
```

## Bracket Entry
The bracket entry submitted simply picks the team with the higher rating. The final score for the tie-breaker was calculated by taking the average points per game of the final 2 teams and rounding up to the nearest integer.

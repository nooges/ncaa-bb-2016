#!/bin/bash

# Download data for NCAA Division I
curl "http://www.masseyratings.com/scores.php?s=284067&sub=11590&all=1&mode=3&format=1" -o data/games_2016.csv
curl "http://www.masseyratings.com/scores.php?s=284067&sub=11590&all=1&mode=3&format=2" -o data/teams_2016.csv

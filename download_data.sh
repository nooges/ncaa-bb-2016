#!/bin/bash

curl "http://www.masseyratings.com/scores.php?s=284067&sub=284067&all=1&mode=3&format=1" -o games_2016.csv
curl "http://www.masseyratings.com/scores.php?s=284067&sub=284067&all=1&mode=3&format=2" -o teams_2016.csv

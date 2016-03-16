#!/usr/bin/env python

import csv
from datetime import datetime
from pprint import pprint

# Iterate through each game and compute rating
class EloRater(object):
    def __init__(self):
        self.K = 30
        self.initial_rating = 1000
        self.teams = {}
        self.games = []

        self.readTeams('data/teams_2016.csv')
        #pprint(self.teams)

        self.readGames('data/games_2016.csv')
        pprint(self.games)

    def readTeams(self, teams_filename):
        """Read in team names from CSV file"""
        with open(teams_filename) as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                team_id = int(row[0])
                team_name = row[1]
                self.teams[team_id] = {'name': team_name, 'rating': self.initial_rating}

    def readGames(self, games_filename):
        """Read in games from CSV file"""
        homefield_map = {1: 'home', -1: 'away', 0: 'neutral'}
        with open(games_filename) as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                game = {}
                game['date'] = datetime.strptime(row[1], '%Y%m%d')
                game['team1_id'] = int(row[2])
                game['team1_homefield'] = homefield_map[int(row[3])]
                game['team1_score'] = int(row[4])
                game['team2_id'] = int(row[5])
                game['team2_homefield'] = homefield_map[int(row[6])]
                game['team2_score'] = int(row[7])
                self.games.append(game)

    def ratingChange(self, rating1, rating2, score1, score2):
        pass
    
    def computeRatings(self, games):
        pass

rater = EloRater()

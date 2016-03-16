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
        self.team_name_to_id = {}
        self.games = []

        print 'Reading teams'
        self.read_participating_teams('data/tournament_teams.csv')
        self.read_teams('data/teams_2016.csv')
        #pprint(self.teams)

        print 'Reading games'
        self.read_games('data/games_2016.csv')
        #pprint(self.games)

    def read_teams(self, teams_filename):
        """Read in team names from CSV file"""
        with open(teams_filename) as csvfile:
            csvreader = csv.reader(csvfile, skipinitialspace=True)
            for row in csvreader:
                team_id = int(row[0])
                team_name = row[1]
                self.teams[team_id] = {
                    'name': team_name,
                    'rating': self.initial_rating,
                    'opponents': [],
                    'participating': team_name in self.tournament_teams}
                self.team_name_to_id[team_name] = team_id

    def read_games(self, games_filename):
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

                self.teams[game['team1_id']]['opponents'].append(game['team2_id'])
                self.teams[game['team2_id']]['opponents'].append(game['team1_id'])

    def read_participating_teams(self, teams_filename):
        self.tournament_teams = open(teams_filename).read().splitlines()
        pprint(self.tournament_teams)

    def rating_change(self, rating1, rating2, score1, score2):
        """Returns rating change for team 1"""
        expected_win_prob_team1 = 1.0/(1 + 10**((rating2 - rating1)/400))

        # TODO: Compute bonus based on score differential
        bonus = 0

        change = self.K * (1 + bonus) * expected_win_prob_team1
        return change
    
    def compute_ratings(self):
        for n,game in enumerate(self.games):
            team1_id = game['team1_id']
            team1_score = game['team1_score']
            team1_rating = self.teams[team1_id]['rating']
            team2_id = game['team2_id']
            team2_score = game['team2_score']
            team2_rating = self.teams[team2_id]['rating']
            #print team1_rating, team2_rating

            change = self.rating_change(team1_rating, team2_rating, team1_score, team2_score)
            self.teams[team1_id]['rating'] += change
            self.teams[team2_id]['rating'] -= change
            '''
            print '{}: {} ({} + {} = {})\t{} ({} - {} = {})'.format(
                n,
                self.teams[team1_id]['name'],
                int(team1_rating),
                change,
                int(team1_rating + change),
                self.teams[team2_id]['name'],
                int(team2_rating),
                -change,
                int(team2_rating - change))
            '''

    def adjust_for_strength_of_schedule(self):
        """Adjust ratings based on strength of schedule"""
        C = 1.5
        new_ratings = {}
        for team_id, team_info in self.teams.items():
            ratings = map(lambda opponent_id: self.teams[opponent_id]['rating'], team_info['opponents'])
            mean = sum(ratings)/len(ratings)
            #print team_info['name'], int(team_info['rating']), int(mean)
            new_ratings[team_id] = team_info['rating']*(mean**C)/(1000**C)

        for team_id, new_rating in new_ratings.items():
            self.teams[team_id]['rating'] = new_rating

    def print_ratings(self):
        """Print ratings, in descending order"""
        # Filter out teams not in tournament
        tournament_teams = self.teams.items()
        #tournament_teams = filter(lambda team: team[1]['participating'], self.teams.items())

        sorted_ratings = sorted(tournament_teams, key=lambda team: team[1]['rating'], reverse=True)

        print 'Rank\tRating\tTeam'
        for n,team in enumerate(sorted_ratings):
            if team[1]['participating']:
                print '{}\t{}\t{}'.format(
                    n+1,
                    #len(sorted_ratings)-n,
                    int(team[1]['rating']),
                    team[1]['name'].replace('_', ' '),)

rater = EloRater()
print 'Computing Ratings'
rater.compute_ratings()
#rater.print_ratings()
rater.adjust_for_strength_of_schedule()
#rater.compute_ratings()
rater.print_ratings()


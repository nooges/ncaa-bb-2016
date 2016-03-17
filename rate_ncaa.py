#!/usr/bin/env python

import csv
from datetime import datetime
from pprint import pprint
import random

# Iterate through each game and compute rating
class EloRater(object):
    def __init__(self):
        self.K = 30
        self.initial_rating = 1000
        self.teams = {}
        self.team_name_to_id = {}
        self.games = []
        self.max_bonus = 0
        self.regions = ['South', 'East', 'West', 'Midwest']

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
                participating = team_name in self.tournament_teams
                self.teams[team_id] = {
                    'name': team_name,
                    'rating': self.initial_rating,
                    'opponents': [],
                    'participating': participating}
                if participating:
                    self.teams[team_id]['seed'] = self.tournament_teams[team_name]['seed']
                    self.teams[team_id]['region'] = self.tournament_teams[team_name]['region']
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
        self.tournament_teams = {}
        self.seeds = {}
        with open(teams_filename) as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                seed = int(row[0])
                region = row[1]
                team_name = row[2]
                team = {'seed': seed, 'region': region}
                self.tournament_teams[team_name] = team
                region_seeds = self.seeds.get(region, {})
                region_seeds[seed] = team_name
                self.seeds[region] = region_seeds

        pprint(self.tournament_teams)
        pprint(self.seeds)

    def expected_win_probability(self, rating1, rating2):
        return 1.0/(1 + 10**((rating2 - rating1)/400))

    def rating_change(self, rating1, rating2, score1, score2):
        """Returns rating change for team 1"""
        expected_win_prob_team1 = self.expected_win_probability(rating1, rating2)

        # Compute bonus based on score differential
        bonus = 1.0*abs(score1 - score2)/(score1 + score2)
        bonus = bonus**0.5
        self.max_bonus = max(self.max_bonus, bonus)
        #print self.max_bonus,bonus

        change = self.K * (0.4 + bonus) * expected_win_prob_team1
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
            new_ratings[team_id] = team_info['rating']*((mean/1000)**C)

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
                print '{}\t{}\t({}) {}'.format(
                    n+1,
                    #len(sorted_ratings)-n,
                    int(team[1]['rating']),
                    team[1]['seed'],
                    team[1]['name'].replace('_', ' '),)

    def game_id(self, region, round_number, game_number):
        return '{}-{}-{}'.format(region, round_number, game_number)

    def generate_initial_matchups(self):
        self.matchups = {}

        # Round 1
        for region in self.regions:
            for game_number in xrange(8):
                game_id = self.game_id(region, 1, game_number+1)
                seed1 = [1,8,5,4,6,3,7,2][game_number]
                seed2 = 17 - seed1
                game_info = {'team1': self.seeds[region][seed1], 'team2': self.seeds[region][seed2]}
                self.matchups[game_id] = game_info

        pprint(self.matchups)

    def pick_winner(self, game_id, next_game_id):
        matchup = self.matchups[game_id]
        team1_id = self.team_name_to_id[matchup['team1']]
        team2_id = self.team_name_to_id[matchup['team2']]
        team1_seed = self.teams[team1_id]['seed']
        team2_seed = self.teams[team2_id]['seed']
        team1_rating = self.teams[team1_id]['rating']
        team2_rating = self.teams[team2_id]['rating']
        team1_win_probability = self.expected_win_probability(team1_rating, team2_rating)
        winner_selection = random.random()

        # Pick team to win
        winner_name = matchup['team1'] if team1_win_probability > winner_selection else matchup['team2']
        next_matchup = self.matchups.get(next_game_id, {})
        if 'team1' in next_matchup:
            next_matchup['team2'] = winner_name
        else:
            next_matchup['team1'] = winner_name
        self.matchups[next_game_id] = next_matchup

        print '({5}) {0} vs ({6}) {1}: {2:.2f} {3:.2f}, {4}'.format(matchup['team1'], matchup['team2'], team1_win_probability, winner_selection, winner_name, team1_seed, team2_seed)

    def generate_bracket_picks(self):
        random.seed(0)

        for round_number in xrange(1,5):
            print '=== Round {} ==='.format(round_number)
            for region in self.regions:
                print '-- {} --'.format(region)
                games_this_round = 16/(2**round_number)
                for game_number in xrange(games_this_round):
                    game_id = self.game_id(region, round_number, game_number+1)

                    if round_number == 4:
                        next_game_number = 1 if region in ['South', 'West'] else 2
                        next_game_id = self.game_id('Final_Four', 5, next_game_number)
                    else:
                        next_game_id = self.game_id(region, round_number+1, game_number//2 + 1)

                    self.pick_winner(game_id, next_game_id)
            print

        # Final Four
        for round_number in xrange(5,7):
            print '=== Final Four ==='
            region = 'Final_Four'
            games_this_round = 64/(2**round_number)
            for game_number in xrange(games_this_round):
                game_id = self.game_id(region, round_number, game_number+1)
                next_game_id = self.game_id(region, round_number+1, game_number//2 + 1)
                self.pick_winner(game_id, next_game_id)
            print


rater = EloRater()
print 'Computing Ratings'
rater.compute_ratings()
#rater.print_ratings()
rater.adjust_for_strength_of_schedule()
#rater.compute_ratings()
rater.print_ratings()

rater.generate_initial_matchups()
rater.generate_bracket_picks()

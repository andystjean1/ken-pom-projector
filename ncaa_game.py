from game import Game
from team import Team

class NcaaGame(Game):
    def __init__(self, home_team:Team, away_team:Team, total:float, line:float):
        super().__init__(home_team, away_team, total, line)

        self.home_projected_score = 0
        self.away_projected_score = 0
        self.projected_total = 0
        self.projected_line = 0
        self.total_edge = 0
        self.line_edge = 0
        self.total_pick = ""
        self.line_pick = ""

    #project the score with a more mathy formula
    def project_score(self, league_avg_pace, league_avg_ppg):

        #check if the team stats are empty
        if(isinstance(self.home_team.stats, int) or isinstance(self.away_team.stats, int)):
            print("The Game for {} and {} didnt not have any stats".format(self.home_team.name, self.away_team.name))

        else:

            #adjust for home court advantage
            home_adj_off = round(self.home_team.adjusted_offense() * 1.014, 2) #add 1.4% to the home team offense
            home_adj_def = round(self.home_team.adjusted_defense() * 0.986, 2) #subtract 1.4% to the home team defense

            away_adj_off = round(self.away_team.adjusted_offense() * 0.986, 2) #subtract 1.4% to the away team offense
            away_adj_def = round(self.away_team.adjusted_defense() * 1.014, 2) #add 1.4% to teh away team defense

            #caluclate the self pace
            self_pace = (self.home_team.adjusted_tempo() * self.away_team.adjusted_tempo())/league_avg_pace #multiply ken pom pace from each team and divide by the league average
            self_pace = round(self_pace, 2)

            #calculate the PPP for each team
            home_ppp = round((home_adj_off * away_adj_def)/league_avg_ppg, 2)
            away_ppp = round((away_adj_off * home_adj_def)/league_avg_ppg, 2)

            #multuply the PPP by the self pace and divide by 100
            home_points = (home_ppp * self_pace)/100
            away_points = (away_ppp * self_pace)/100

            self.home_projected_score = round(home_points, 2)
            self.away_projected_score = round(away_points, 2)
            self.projected_total = round(home_points + away_points, 2)
            self.projected_line = round(abs(home_points - away_points), 2)

            self.calculate_edge()
    
    def project_score_tourney(self, league_avg_pace, league_avg_ppg):

        #check if the team stats are empty
        if(isinstance(self.home_team.stats, int) or isinstance(self.away_team.stats, int)):
            print("The Game for {} and {} didnt not have any stats".format(self.home_team.name, self.away_team.name))

        else:

            #adjust for home court advantage
            home_adj_off = round(self.home_team.adjusted_offense())# * 1.014, 2) #add 1.4% to the home team offense
            home_adj_def = round(self.home_team.adjusted_defense())# * 0.986, 2) #subtract 1.4% to the home team defense

            away_adj_off = round(self.away_team.adjusted_offense() * 0.986, 2) #subtract 1.4% to the away team offense
            away_adj_def = round(self.away_team.adjusted_defense() * 1.014, 2) #add 1.4% to teh away team defense

            #caluclate the self pace
            self_pace = (self.home_team.adjusted_tempo() * self.away_team.adjusted_tempo())/league_avg_pace #multiply ken pom pace from each team and divide by the league average
            self_pace = round(self_pace, 2)

            #calculate the PPP for each team
            home_ppp = round((home_adj_off * away_adj_def)/league_avg_ppg, 2)
            away_ppp = round((away_adj_off * home_adj_def)/league_avg_ppg, 2)

            #multuply the PPP by the self pace and divide by 100
            home_points = (home_ppp * self_pace)/100
            away_points = (away_ppp * self_pace)/100

            self.home_projected_score = round(home_points, 2)
            self.away_projected_score = round(away_points, 2)
            self.projected_total = round(home_points + away_points, 2)
            self.projected_line = round(abs(home_points - away_points), 2)

            self.calculate_edge()
    
    #calculate the edge
    def calculate_edge(self):
        #subtract the total from the projected and multiply by -1 to flip the number to match over/under
        self.total_edge = (self.total - self.projected_total) * -1

        #populate the pick for the total
        if(self.total > self.projected_total):
            self.total_pick = "under"

        if(self.total < self.projected_total):
            self.total_pick = "over"

        #calculate the line edge
        self.line_edge = self.line - self.projected_line

        if(self.line < self.projected_line):
            self.line_pick = "fav"
        if(self.line > self.projected_line):
            self.line_pick = "dog"

    #generate a dictionary for a dataframe
    def generate_dictionary(self) -> dict: 
        return {"home_team": self.home_team.name,
                "away_team": self.away_team.name,
                "home_projected_score": self.home_projected_score,
                "away_projected_score": self.away_projected_score,
                "projected_total": self.projected_total,
                "total": self.total,
                "projected_line": self.projected_line,
                "line":self.line,
                "line_edge":self.line_edge,
                "total_edge":self.total_edge,
                "total_pick":self.total_pick,
                "line_pick":self.line_pick
                }

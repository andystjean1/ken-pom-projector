
from team import Team

#Game class
class Game(object):
    def __init__(self, home_team:Team, away_team:Team, total:float, line:float):
        self.home_team = home_team
        self.away_team = away_team
        self.total = total
        self.line = line
        self.home_projected_score = 0
        self.away_projected_score = 0
        self.projected_total = 0
        self.projected_line = 0
        self.total_edge = 0
        self.line_edge = 0
        self.total_pick = ""
        self.line_pick = ""

    #project the game score
    def project_score(self):
        t1_off_pts = (self.home_team.adjusted_offense()/100) * self.home_team.adjusted_tempo()
        t1_def_pts = (self.home_team.adjusted_defense()/100) * self.home_team.adjusted_tempo()

        t2_off_pts = (self.away_team.adjusted_offense()/100) * self.home_team.adjusted_tempo()
        t2_def_pts = (self.away_team.adjusted_defense()/100) * self.away_team.adjusted_tempo()

        t1_score = round(((t1_off_pts + t2_def_pts))/2, 2)
        t2_score = round(((t2_off_pts + t1_def_pts))/2, 2)

        self.home_projected_score = t1_score
        self.away_projected_score = t2_score
        self.projected_total = t1_score + t2_score
        self.projected_line = abs(t1_score - t2_score)
    
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

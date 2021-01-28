
from team import Team

#Game class
class Game(object):
    def __init__(self, home_team:Team, away_team:Team, total:float, line:float):
        self.home_team = home_team
        self.away_team = away_team
        self.total = total
        self.line = line
    

    

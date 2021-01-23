
import pandas as pd

#Team class 
class Team(object):
    def __init__(self, team_name:str, team_stats):
        if(not(team_stats.empty)):
            self.name = team_name
            self.stats = team_stats
        else:
            print("couldnt find kenpom stats for", team_name)
            self.name = team_name
            self.stats = -1
            

    #return the adjusted tempo stat
    def adjusted_tempo(self):
        return self.stats.iloc[0]["AdjT"]
    
    #return the adjusted offense stat
    def adjusted_offense(self):
        return self.stats.iloc[0]["AdjO"]
    
    #return the adjusted defense stat
    def adjusted_defense(self):
        return self.stats.iloc[0]["AdjD"]

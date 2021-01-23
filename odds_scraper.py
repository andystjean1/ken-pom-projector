
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
import statistics

#custom modules
from scraper import scrape_ken_pom

#Make ken_pom_df global so the team class can access it
ken_pom_df = scrape_ken_pom()
league_avg_ppg = scrape_possession_data()

tr_url = "https://www.teamrankings.com/ncb/odds/"
tr_possessions_url = "https://www.teamrankings.com/ncaa-basketball/stat/possessions-per-game" #omitting the data parameter will get the page for the current date
tr_points_per_game_url = "https://www.teamrankings.com/ncaa-basketball/stat/points-per-game"


#Team class 
class Team(object):
    def __init__(self, team_name:str, team_stats):
        if(not(team_stats.empty)):
            self.name = team_name
            self.stats = team_stats
        else:
            print("couldnt find kenpom stats for", team_name)

    #return the adjusted tempo stat
    def adjusted_tempo(self):
        return self.stats.iloc[0]["AdjT"]
    
    #return the adjusted offense stat
    def adjusted_offense(self):
        return self.stats.iloc[0]["AdjO"]
    
    #return the adjusted defense stat
    def adjusted_defense(self):
        return self.stats.iloc[0]["AdjD"]

#Game class
class Game(object):
    def __init__(self, home_team:Team, away_team:Team, total:float):
        self.home_team = home_team
        self.away_team = away_team
        self.total = total
        self.home_projected_score = 0
        self.away_projected_score = 0
        self.projected_total = 0
        self.edge = 0

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
    
    #calculate the edge
    def calculate_edge(self):
        #subtract the total from the projected and multiply by -1 to flip the number to match over/under
        self.edge = (self.total - self.projected_total) * -1

    #generate a dictionary for a dataframe
    def generate_dictionary(self) -> dict: 
        return {"home_team": self.home_team.name,
                "away_team": self.away_team.name,
                "home_projected_score": self.home_projected_score,
                "away_projected_score": self.away_projected_score,
                "projected_total": self.projected_total,
                "total": self.total,
                "edge":self.edge
                }


#scrape the games from team rankings
def scrape_game_tables():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(tr_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()

    div = soup.find('div', attrs={"class":"module-in clear"})
    tables = div.find_all("table")

    return tables

#scrape the league average possession from team rankings
def scrape_possession_data():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(tr_possessions_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()

    table = soup.find('table', attrs={"id":"DataTables_Table_0"})
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    for row in rows:
        data = row.find_all('td')
        ppg = data[2].text
        ppg_data = [row.find_all('td')[2].text for row in rows]
        ppg = [float(ppg) for ppg in ppg_data if ppg != "--"]

    return statistics.mean(ppg)

    

#scrape the league average points per game from team rankings
def scrape_points_per_game_data():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(tr_points_per_game_url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()

    table = soup.find('table', attrs={"id":"DataTables_Table_0"})
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    for row in rows:
        data = row.find_all('td')
        ppg = data[2].text
        ppg_data = [row.find_all('td')[2].text for row in rows]
        ppg = [float(ppg) for ppg in ppg_data if ppg != "--"]

    return statistics.mean(ppg)


# convert an html game into an object
# grab the two teams playing and the total line
def convert_html_to_game(table) -> Game: 
    #grab the rows from the tables
    rows = table.find("tbody").find_all("tr")

    #grab the team names and total 
    away_name = rows[0].find_all('td')[0].text.strip()
    home_name = rows[1].find_all('td')[0].text.strip()

    #find the ken pom stats for team 1 and create the team object
    home_stats = ken_pom_df[ken_pom_df["Team"] == home_name]
    home = Team(home_name, home_stats)

    #find the ken pom stats for team 2 and create the team object
    away_stats = ken_pom_df[ken_pom_df["Team"] == away_name]
    away = Team(away_name, away_stats)

    total = float(rows[0].find_all('td')[3].text.strip())

    # return a new game object
    return Game(home, away, total)
    
#MAIN FUCNTION
if __name__ == "__main__":
    cols = ["home_team", "away_team", "home_projected_score", "away_projected_score", "projected_total", "total", "edge"]
    game_df = pd.DataFrame(columns=cols)

    tables = scrape_game_tables()
    #convert the html into game objects
    games = [convert_html_to_game(table) for table in tables]

    for game in games:
        #project the game score and calculate the edge
        game.project_score()
        game.calculate_edge()

        #write the game to a data frame
        game_df = game_df.append(game.generate_dictionary(), ignore_index=True)
    
    
    game_df.to_excel("output.xlsx")

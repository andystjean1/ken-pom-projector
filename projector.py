from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd 

from scraper import scrape_ken_pom
from scraper import scrape_game_tables
from scraper import scrape_game_table_tomorrow
from scraper import scrape_points_per_game_avg
from scraper import scrape_games_tourney
from scraper import scrape_possession_avg
from scraper import generate_test_game
from scraper import scrape_adjusted_off_avg
from scraper import convert_html_to_game

from game import Game

#urls to use
tr_odds_url = "https://www.teamrankings.com/ncb/odds/"
tr_possessions_url = "https://www.teamrankings.com/ncaa-basketball/stat/possessions-per-game" #omitting the data parameter will get the page for the current date
tr_points_per_game_url = "https://www.teamrankings.com/ncaa-basketball/stat/points-per-game"

#initialize the data for the projector
def initialize_data(day:str):
    
    #some global variables
    global league_avg_pace 
    global league_avg_ppg 
    global games 
    
    driver = webdriver.Chrome(ChromeDriverManager().install())

    league_avg_pace = scrape_possession_avg(driver, tr_possessions_url)
    league_avg_ppg = scrape_adjusted_off_avg() 

    if(day == "today"):
        games_table = scrape_game_tables(driver, tr_odds_url)
        games = [convert_html_to_game(table) for table in games_table]
    elif(day == "tomorrow"):
        games_table = scrape_game_table_tomorrow(driver, tr_odds_url)
        games = [convert_html_to_game(table) for table in games_table]
    else:
        print(day + " is not a valid day")
        games = []

    driver.close()

#initialize data for march madness
def initialize_tourney():
     #some global variables
    global league_avg_pace 
    global league_avg_ppg 
    global games 
    
    driver = webdriver.Chrome(ChromeDriverManager().install())

    league_avg_pace = scrape_possession_avg(driver, tr_possessions_url)
    league_avg_ppg = scrape_adjusted_off_avg() 

    
    games_table = scrape_games_tourney(driver, tr_odds_url)

    for table in games_table:
        matches = [convert_html_to_game(t) for t in table]
        games.append(matches)

    driver.close()


#initialize data for debugging
def initialize_debug_data():

    global league_avg_pace
    global league_avg_ppg
    global games

    league_avg_pace = 67.6
    league_avg_ppg = 100
    games = generate_test_game()

#project the game score with basic offense and defense
def project_score_basic(game:Game):
    #divide the adjO and adjD to get points per possession and multiply by the adjT
    t1_off_pts = (game.home_team.adjusted_offense()/100) * game.home_team.adjusted_tempo()
    t1_def_pts = (game.home_team.adjusted_defense()/100) * game.home_team.adjusted_tempo()

    t2_off_pts = (game.away_team.adjusted_offense()/100) * game.home_team.adjusted_tempo()
    t2_def_pts = (game.away_team.adjusted_defense()/100) * game.away_team.adjusted_tempo()

    #add the teams offensive points to their defensive points and divide by 2 to get the score
    t1_score = round(((t1_off_pts + t2_def_pts))/2, 2)
    t2_score = round(((t2_off_pts + t1_def_pts))/2, 2)

    game.home_projected_score = t1_score
    game.away_projected_score = t2_score
    game.projected_total = t1_score + t2_score
    game.projected_line = abs(t1_score - t2_score)

    #calculate the edge with the projected totals
    game.calculate_edge()

#project the score with a more mathy formula
def project_score_advanced(gane:Game):

    #check if the team stats are empty
    if(isinstance(game.home_team.stats, int) or isinstance(game.away_team.stats, int)):
        print("The Game for {} and {} didnt not have any stats".format(game.home_team.name, game.away_team.name))

    else:

        #adjust for home court advantage
        home_adj_off = round(game.home_team.adjusted_offense() * 1.014, 2) #add 1.4% to the home team offense
        home_adj_def = round(game.home_team.adjusted_defense() * 0.986, 2) #subtract 1.4% to the home team defense

        away_adj_off = round(game.away_team.adjusted_offense() * 0.986, 2) #subtract 1.4% to the away team offense
        away_adj_def = round(game.away_team.adjusted_defense() * 1.014, 2) #add 1.4% to teh away team defense

        #caluclate the game pace
        game_pace = (game.home_team.adjusted_tempo() * game.away_team.adjusted_tempo())/league_avg_pace #multiply ken pom pace from each team and divide by the league average
        game_pace = round(game_pace, 2)

        #calculate the PPP for each team
        home_ppp = round((home_adj_off * away_adj_def)/league_avg_ppg, 2)
        away_ppp = round((away_adj_off * home_adj_def)/league_avg_ppg, 2)

        #multuply the PPP by the game pace and divide by 100
        home_points = (home_ppp * game_pace)/100
        away_points = (away_ppp * game_pace)/100

        game.home_projected_score = round(home_points, 2)
        game.away_projected_score = round(away_points, 2)
        game.projected_total = round(home_points + away_points, 2)
        game.projected_line = round(abs(home_points - away_points), 2)

        game.calculate_edge()

#project the score with a more mathy formula
def project_score_tourney(gane:Game):

    #check if the team stats are empty
    if(isinstance(game.home_team.stats, int) or isinstance(game.away_team.stats, int)):
        print("The Game for {} and {} didnt not have any stats".format(game.home_team.name, game.away_team.name))

    else:
        #caluclate the game pace
        game_pace = (game.home_team.adjusted_tempo() * game.away_team.adjusted_tempo())/league_avg_pace #multiply ken pom pace from each team and divide by the league average
        game_pace = round(game_pace, 2)

        #calculate the PPP for each team
        home_ppp = round((home_adj_off * away_adj_def)/league_avg_ppg, 2)
        away_ppp = round((away_adj_off * home_adj_def)/league_avg_ppg, 2)

        #multuply the PPP by the game pace and divide by 100
        home_points = (home_ppp * game_pace)/100
        away_points = (away_ppp * game_pace)/100

        game.home_projected_score = round(home_points, 2)
        game.away_projected_score = round(away_points, 2)
        game.projected_total = round(home_points + away_points, 2)
        game.projected_line = round(abs(home_points - away_points), 2)

        game.calculate_edge()

#MAIN FUNCTION
if __name__ == "__main__":

    #initialize the dataframe
    cols = ["home_team", "away_team", "home_projected_score", "away_projected_score", "projected_total", "total", "projected_line", "line","line_edge","total_edge","total_pick", "line_pick"]
    game_df = pd.DataFrame(columns=cols)

    #populate the global data variables
    #initialize_data("today")
    #initialize_debug_data()
    initialize_tourney()

    print("initialized data")
    print(len(games))

    #project the score for each game
    for game in games:


        #game.project_score(league_avg_pace, league_avg_ppg)
        game_df = game_df.append(game.generate_dictionary(), ignore_index=True)

    game_df.to_excel("output.xlsx")










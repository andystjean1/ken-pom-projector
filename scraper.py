import pandas as pd
from bs4 import BeautifulSoup
import requests
from os import path
import re
import time
import statistics
import math

from ncaa_game import NcaaGame
from game import Game
from team import Team

###################################
# SCRAP KEN POM
###################################
def scrape_ken_pom():
    
    url="https://kenpom.com/index.php"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')

    #find the table and header tags
    table = soup.find_all('table', {'id':'ratings-table'})[0]
    headers = table.find('thead').find('tr', {'class':'thead2'})
    #store the header tags titles into a list
    cols = [th.text for th in headers.find_all('th')]

    #initialize the dataframe
    
    kenpom_df = pd.DataFrame(columns=cols)

    #get the data elements from the table
    body = table.find_all('tbody')[0]
    rows = body.find_all('tr')

    #scrape the data from each row
    for r in rows:
        data = r.find_all('td')
        info = []

        for d in data:
            try:
                if(d["class"] != ['td-right']):
                    info.append(d.text)
            except:
                info.append(d.text)

        #if the list isnt empty
        if(info != []):
            #create a series with the list and add it to the dataframe
            info_df = pd.Series(info, index=cols)
            kenpom_df = kenpom_df.append(info_df, ignore_index=True)

    #clean and convert columns
    kenpom_df["Team"] = kenpom_df.apply(lambda row: format_state_names(row), axis=1)
    kenpom_df["AdjO"] = pd.to_numeric(kenpom_df["AdjO"])
    kenpom_df["AdjD"] = pd.to_numeric(kenpom_df["AdjD"])
    kenpom_df["AdjT"] = pd.to_numeric(kenpom_df["AdjT"])

    return kenpom_df

#Team Name Dictionary to make everything matchy matchy
TEAM_NAME_DICT = {"The Citadel":"Citadel",
                  "VMI":"VA Military",
                  "Miami FL":"Miami (FL)",
                  "UTSA":"TX-San Ant",
                  "FIU":"Florida Intl",
                  "Southern Miss":"S Mississippi",
                  "Middle Tennessee":"Middle Tenn",
                  "Miami OH":"Miami (OH)",
                  "St. Francis NY": "St Fran (NY)",
                  "Loyola MD":"Loyola-MD",
                  "Bethune Cookman":"Bethune-Cookman",
                  "Nebraska Omaha":"Neb Omaha",
                  "New Hampshire":"N Hampshire",
                  "Gardner Webb":"Gard-Webb",
                  "N.C. State":"NC State",
                  "Maryland Eastern Shore":"Maryland-Eastern Shore",
                  "St. Francis PA":"St Fran (PA)",
                  "Mount St Mary's":"Mt St Marys",
                  "Texas A&M Corpus Chris":"TX A&M-CC",
                  "Tennessee Martin":"TN Martin",
                  "SIU Edwardsville":"SIU Edward",
                  "TCU":"TX Christian",
                  "Penn":"Pennsylvania",
                  "SMU":"S Methodist",
                  "Arkansas Pine Bluff":"Ark Pine Bl",
                  "UT Rio Grande Valley":"TX-Pan Am",
                  "Loyola Chicago":"Loyola-Chi",
                  "Western Kentucky":"W Kentucky",
                  "North Dakota St": "N Dakota St",
                  "South Dakota St": "S Dakota St",
                  "Long Beach St": "Lg Beach St",
                  "San Francisco":"San Fransco",
                  "Northeastern":"Northeastrn",
                  "Massachusetts":"U Mass",
                  "West Virginia":"W Virginia",
                  "St. John's": "St Johns",
                  "UNC Asheville": "NC-Asheville",
                  "Appalachian St":"App State",
                  "George Washington":"Geo Wshgtn",
                  "Georgia Southern":"GA Southern",
                  "South Carolina St":"S Car State",
                  "East Carolina":"E Carolina",
                  "Charleston":"Col Charlestn",
                  "Southern Illinois":"S Illinois",
                  "Milwaukee": "WI-Milwkee",
                  "Grand Canyon":"Grd Canyon",
                  "Iowa St" : "Iowa State",
                  "Saint Mary's":"St Marys",
                  "Florida Gulf Coast":"Fla Gulf Cst",
                  "Tennessee St":"TN State",
                  "South Florida":"S Florida",
                  "Boston College":"Boston Col",
                  "North Carolina":"N Carolina",
                  "South Carolina":"S Carolina",
                  "North Carolina Central":"NC Central",
                  "Western Michigan":"W Michigan",
                  "St. Bonaventure":"St Bonavent",
                  "South Alabama":"S Alabama",
                  "Mississippi St": "Miss State",
                  "Dixie St": "Dixie State",
                  "East Tennessee St":"E Tenn St",
                  "USC Upstate":"SC Upstate",
                  "Utah Valley":"Utah Val St",
                  "North Carolina A&T":"NC A&T",
                  "Western Carolina": "W Carolina",
                  "Cal St Bakersfield":"CS Bakersfld",
                  "Central Michigan":"Central Mich",
                  "North Florida":"N Florida",
                  "Loyola Marymount":"Loyola Mymt",
                  "UC Santa Barbara":"UCSB",
                  "Sacramento St":"Sac State",
                  "Tarleton St": "Tarleton State",

                  "Eastern Illinois":"E Illinois",
                  "Western Illinois":"W Illinois",
                  "Louisiana Monroe":"LA Monroe",
                  "Stephen F. Austin":"Ste F Austin",
                  "UNC Wilmington":"NC-Wilmgton",
                  "UTEP":"TX El Paso",
                  "Ball St":"Ball State",
                  "Louisiana Tech":"LA Tech",
                  "Central Arkansas":"Central Ark",
                  "Cal St Northridge":"Cal St Nrdge",
                  "Louisiana":'LA Lafayette',
                  "Tennessee Tech":"TN Tech",
                  "Jacksonville St":"Jksnville St",
                  "Washingston St":"Wash State",
                  "Sam Houston St":"Sam Hous St",
                  "Eastern Kentucky":"E Kentucky",
                  "William & Mary":"Wm & Mary",
                  "Northern Arizona":"N Arizona",
                  "Northern Colorado":"N Colorado",
                  "Houston Baptist":"Houston Bap",
                  "Central Connecticut":"Central Conn",
                  "Coastal Carolina":"Coastal Car",
                  "Virginia Tech":"VA Tech",
                  "Texas Southern":"TX Southern",
                  "UNC Greensboro":"NC-Grnsboro",
                  "Florida Atlantic":"Fla Atlantic",
                  "Fairleigh Dickinson":"F Dickinson",
                  "Southeastern Louisiana":"SE Louisiana",
                  "Southeast Missouri St":"SE Missouri",
                  "Texas St":"Texas State",
                  "Georgia Tech":"GA Tech",
                  "Eastern Washington":"E Washingtn",
                  "Sacred Heart":"Sacred Hrt",
                  "Ohio St":"Ohio State",
                  "Saint Joseph's":"St Josephs",
                  "Southern Utah":"S Utah",
                  "UMass Lowell":"Mass Lowell",
                  "UCF":"Central FL",
                  "James Madison":"James Mad",
                  "Idaho St":"Idaho State",
                  "Abilene Christian":"Abl Christian",
                  "Charleston Southern":"Charl South",
                  "Northwestern St":"NW State",
                  "George Mason":"Geo Mason",
                  "Washington St":"Wash State",
                  "Penn St":"Penn State",
                  "Weber St":"Weber State",
                  "Coppin St":"Coppin State",
                  "Utah St":"Utah State",
                  "Boise St":"Boise State",
                  "Wright St":"Wright State",
                  "Green Bay":"WI-Grn Bay",
                  "Purdue Fort Wayne":"IPFW",
                  "Youngstown St":"Youngs St",
                  "Illinois Chicago":"IL-Chicago",
                  "Robert Morris":"Rob Morris",
                  "Northern Kentucky":"N Kentucky",
                  "UT Arlington":"TX-Arlington",
                  "Little Rock":"AR Lit Rock",
                  "Saint Peter's":"St Peters",
                  "North Alabama":"N Alabama",
                  "Alabama A&M":"Alab A&M",
                  "Incarnate Word":"Incar Word",
                  "Cal St Fullerton":"CS Fullerton",
                  "Kent St":"Kent State",
                  "Bowling Green":"Bowling Grn",
                  "New Mexico St":"N Mex State"

                }

#format the state
def format_state_names(row):
    name = row.Team
    name = name.replace(" St.", " St")

    try:
        name = TEAM_NAME_DICT[name]
    except:
        pass

    return name

# convert an html game into an object
# grab the two teams playing and the total line
def convert_html_to_game(table) -> Game: 

    #scrape the ken_pom info
    ken_pom_df = scrape_ken_pom()

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

    #find the total for the game
    total = float(rows[0].find_all('td')[3].text.strip())

    #find the line to the game
    line_raw = rows[0].find_all('td')[2].text.strip()
    
    if(line_raw == "(Pick)"):
        line = 0
    else:
        line = abs(float(line_raw))

    # return a new game object
    return NcaaGame(home, away, total, line)

#scrape the games from team rankings
def scrape_game_tables(driver, url):
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    div = soup.find('div', attrs={"class":"module-in clear"})
    tables = div.find_all("table")

    return tables

#scrape the games from team rankings for tomorrow
def scrape_game_table_tomorrow(driver, url):
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    div = soup.find_all('div', attrs={"class":"module-in clear"})[1]
    tables = div.find_all("table")

    print(tables[1])

    return tables

#scrape the league average possession from team rankings
def scrape_possession_avg(driver, url):
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    table = soup.find('table', attrs={"id":"DataTables_Table_0"})
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    for row in rows:
        data = row.find_all('td')
        ppg = data[2].text
        ppg_data = [row.find_all('td')[2].text for row in rows]
        ppg = [float(ppg) for ppg in ppg_data if ppg != "--"]

    return statistics.mean(ppg)

#scrape the league average points scored per game from team rankings
def scrape_points_per_game_avg(driver, url):
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    table = soup.find('table', attrs={"id":"DataTables_Table_0"})
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    for row in rows:
        data = row.find_all('td')
        ppg = data[2].text
        ppg_data = [row.find_all('td')[2].text for row in rows]
        ppg = [float(ppg) for ppg in ppg_data if ppg != "--"]

    return statistics.mean(ppg)

#scrape teh average adjusted offense effeciency
def scrape_adjusted_off_avg():
    kenpom_df = scrape_ken_pom()
    active_teams = kenpom_df[kenpom_df["W-L"] != "0-0"]
    return active_teams["AdjO"].mean()

#def generate test game for testing
def generate_test_game():
    test_df = pd.DataFrame(columns=["Team", "AdjO", "AdjD", "AdjT"])

    #the test data
    duke_dict = {
        "Team":"Duke",
        "AdjO":115.4,
        "AdjD":80.7,
        "AdjT":71.5
    }

    unc_dict = {
        "Team":"UNC",
        "AdjO":119.8,
        "AdjD":87.6,
        "AdjT":76.3
    }

    #add it to the dictionary
    test_df = test_df.append(duke_dict, ignore_index=True)
    test_df = test_df.append(unc_dict, ignore_index=True)

    #duke is the home team - unc is the away team
    duke_stats = test_df[test_df["Team"] == "Duke"]
    duke = Team("Duke", duke_stats)

    unc_stats = test_df[test_df["Team"] == "UNC"]
    unc = Team("UNC", unc_stats)

    test_game = Game(duke, unc, 150.0, 5) #the total here is arbitrary for now

    return [test_game]

if __name__ == "__main__":

    avg_adj_off = scrape_adjusted_off_avg()

    print(avg_adj_off)
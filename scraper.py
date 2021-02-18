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
# SCRAPE KEN POM
###################################
def scrape_ken_pom():
    url="https://kenpom.com/index.php"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')

    #find the table and header tags and store them in a list
    table = soup.find_all('table', {'id':'ratings-table'})[0]
    headers = table.find('thead').find('tr', {'class':'thead2'})
    cols = [th.text for th in headers.find_all('th')]

    kenpom_df = pd.DataFrame(columns=cols)

    #get the data elements from the table and process each row
    body = table.find_all('tbody')[0]
    rows = body.find_all('tr')

    for r in rows:
        data = r.find_all('td')
        info = []

        for d in data:
            try:
                if(d["class"] != ['td-right']):
                    info.append(d.text)
            except:
                info.append(d.text)

        if(info != []):
            info_df = pd.Series(info, index=cols)
            kenpom_df = kenpom_df.append(info_df, ignore_index=True)

    #clean and convert columns
    #kenpom_df["Team"] = kenpom_df.apply(lambda row: format_state_names(row), axis=1)
    kenpom_df["AdjO"] = pd.to_numeric(kenpom_df["AdjO"])
    kenpom_df["AdjD"] = pd.to_numeric(kenpom_df["AdjD"])
    kenpom_df["AdjT"] = pd.to_numeric(kenpom_df["AdjT"])

    return kenpom_df

#Team Name Dictionary to make everything matchy matchy
TEAM_NAME_DICT = {'San Diego St':'San Diego St.','Wichita St':'Wichita St.','Illinois St':'Illinois St.', 'Murray St':'Murray St.','Oregon St':'Oregon St.','Freson St':'Freson St.','Portland St':'Portland St.','Kansas St':'Kansas St.', 'Nicholls St':'Nicholls St.', 'Arizona St':'Arizona St.','Missouri St':'Missouri St.','Citadel': 'The Citadel', 'VA Military': 'VMI', 'Miami (FL)': 'Miami FL', 'TX-San Ant': 'UTSA', 'Florida Intl': 'FIU', 'S Mississippi': 'Southern Miss', 'Middle Tenn': 'Middle Tennessee', 'Miami (OH)': 'Miami OH', 'St Fran (NY)': 'St. Francis NY', 'Loyola-MD': 'Loyola MD', 'Bethune-Cookman': 'Bethune Cookman', 'Neb Omaha': 'Nebraska Omaha', 'N Hampshire': 'New Hampshire', 'Gard-Webb': 'Gardner Webb', 'NC State': 'N.C. St.ate', 'Maryland-Eastern Shore': 'Maryland Eastern Shore', 'St Fran (PA)': 'St. Francis PA', 'Mt St Marys': "Mount St. Mary's", 'TX A&M-CC': 'Texas A&M Corpus Chris', 'TN Martin': 'Tennessee Martin', 'SIU Edward': 'SIU Edwardsville', 'TX Christian': 'TCU', 'Pennsylvania': 'Penn', 'S Methodist': 'SMU', 'Ark Pine Bl': 'Arkansas Pine Bluff', 'TX-Pan Am': 'UT Rio Grande Valley', 'Loyola-Chi': 'Loyola Chicago', 'W Kentucky': 'Western Kentucky', 'N Dakota St': 'North Dakota St.', 'S Dakota St': 'South Dakota St.', 'Lg Beach St': 'Long Beach St.', 'San Fransco': 'San Francisco', 'Northeastrn': 'Northeastern', 'U Mass': 'Massachusetts', 'W Virginia': 'West Virginia', 'St Johns': "St. John's", 'Maryland BC': 'UMBC', 'NC-Asheville': 'UNC Asheville', 'App State': 'Appalachian St.', 'Geo Wshgtn': 'George Washington', 'GA Southern': 'Georgia Southern', 'S Car State': 'South Carolina St.', 'E Carolina': 'East Carolina', 'Col Charlestn': 'Charleston', 'S Illinois': 'Southern Illinois', 'Boston U': 'Boston University', 'WI-Milwkee': 'Milwaukee', 'Grd Canyon': 'Grand Canyon', 'Iowa State': 'Iowa St.', 'St Marys': "Saint Mary's", 'Fla Gulf Cst': 'Florida Gulf Coast', 'TN State': 'Tennessee St.', 'S Florida': 'South Florida', 'Boston Col': 'Boston College', 'N Carolina': 'North Carolina', 'S Carolina': 'South Carolina', 'NC Central': 'North Carolina Central', 'W Michigan': 'Western Michigan', 'St Bonavent': 'St. Bonaventure', 'S Alabama': 'South Alabama', 'Miss State': 'Mississippi St.', 'Dixie State': 'Dixie St.', 'E Tenn St': 'East Tennessee St.', 'SC Upstate': 'USC Upstate', 'Utah Val St': 'Utah Valley', 'NC A&T': 'North Carolina A&T', 'W Carolina': 'Western Carolina', 'CS Bakersfld': 'Cal St. Bakersfield', 'Central Mich': 'Central Michigan', 'N Florida': 'North Florida', 'Loyola Mymt': 'Loyola Marymount', 'UCSB': 'UC Santa Barbara', 'Sac State': 'Sacramento St.', 'Tarleton State': 'Tarleton St.', 'E Illinois': 'Eastern Illinois', 'W Illinois': 'Western Illinois', 'LA Monroe': 'Louisiana Monroe', 'Ste F Austin': 'Stephen F. Austin', 'NC-Wilmgton': 'UNC Wilmington', 'TX El Paso': 'UTEP', 'Ball State': 'Ball St.', 'LA Tech': 'Louisiana Tech', 'Central Ark': 'Central Arkansas', 'Cal St Nrdge': 'Cal St. Northridge', 'LA Lafayette': 'Louisiana', 'TN Tech': 'Tennessee Tech', 'Jksnville St': 'Jacksonville St.', 'Wash State': 'Washington St.', 'Sam Hous St': 'Sam Houston St.', 'E Kentucky': 'Eastern Kentucky', 'Wm & Mary': 'William & Mary', 'N Arizona': 'Northern Arizona', 'N Colorado': 'Northern Colorado', 'Houston Bap': 'Houston Baptist', 'Central Conn': 'Central Connecticut', 'Coastal Car': 'Coastal Carolina', 'VA Tech': 'Virginia Tech', 'TX Southern': 'Texas Southern', 'NC-Grnsboro': 'UNC Greensboro', 'Fla Atlantic': 'Florida Atlantic', 'F Dickinson': 'Fairleigh Dickinson', 'SE Louisiana': 'Southeastern Louisiana', 'SE Missouri': 'Southeast Missouri St.', 'Texas State': 'Texas St.', 'GA Tech': 'Georgia Tech', 'E Washingtn': 'Eastern Washington', 'Sacred Hrt': 'Sacred Heart', 'Ohio State': 'Ohio St.', 'St Josephs': "Saint Joseph's", 'S Utah': 'Southern Utah', 'Mass Lowell': 'UMass Lowell', 'Central FL': 'UCF', 'James Mad': 'James Madison', 'Idaho State': 'Idaho St.', 'Abl Christian': 'Abilene Christian', 'Charl South': 'Charleston Southern', 'NW State': 'Northwestern St.', 'Geo Mason': 'George Mason', 'Penn State': 'Penn St.', 'Weber State': 'Weber St.', 'Coppin State': 'Coppin St.', 'Utah State': 'Utah St.', 'Boise State': 'Boise St.', 'Wright State': 'Wright St.', 'WI-Grn Bay': 'Green Bay', 'IPFW': 'Purdue Fort Wayne', 'Youngs St': 'Youngstown St.', 'IL-Chicago': 'Illinois Chicago', 'Rob Morris': 'Robert Morris', 'N Kentucky': 'Northern Kentucky', 'TX-Arlington': 'UT Arlington', 'AR Lit Rock': 'Little Rock', 'St Peters': "Saint Peter's", 'N Alabama': 'North Alabama', 'Alab A&M': 'Alabama A&M', 'Incar Word': 'Incarnate Word', 'CS Fullerton': 'Cal St. Fullerton', 'Kent State': 'Kent St.', 'Bowling Grn': 'Bowling Green', 'N Mex State': 'New Mexico St.', 'Miss Val St': 'Mississippi Valley St.', 'N Iowa': 'Northern Iowa', 'Alcorn State': 'Alcorn St.', 'Prairie View': 'Prairie View A&M'}


#map a team ranking team name to kenpom
def map_name_to_kenpom(name_tr: str) -> str:
    name_kp = name_tr
    try:
        name_kp = TEAM_NAME_DICT[name_tr]
    except KeyError:
        pass

    #if no name is found return the original name
    return name_kp

# convert an html game into an object
# grab the two teams playing and the total line
def convert_html_to_game(table) -> Game: 

    #scrape the ken_pom info - WHY AM I SCRAPING KEN POM EVERYTIME I CONVERT A GAME
    ken_pom_df = scrape_ken_pom()

    #grab the rows from the tables
    rows = table.find("tbody").find_all("tr")

    #grab the team names
    away_name_tr = rows[0].find_all('td')[0].text.strip()
    home_name_tr = rows[1].find_all('td')[0].text.strip()

    #map the names here
    away_name_kp = map_name_to_kenpom(away_name_tr)
    home_name_kp = map_name_to_kenpom(home_name_tr)

    #find the ken pom stats for team 1 and create the team object
    home_stats = ken_pom_df[ken_pom_df["Team"] == home_name_kp]
    home = Team(home_name_kp, home_stats)

    #find the ken pom stats for team 2 and create the team object
    away_stats = ken_pom_df[ken_pom_df["Team"] == away_name_kp]
    away = Team(away_name_kp, away_stats)

    #find the total for the game
    total_raw = rows[0].find_all('td')[3].text.strip()

    if(total_raw == "--"):
        total = 0
    else:
        total = float(total_raw)

    #find the line to the game
    line_raw = rows[0].find_all('td')[2].text.strip()
    
    if(line_raw == "(Pick)"):
        line = 0
    else:
        try:
            line = abs(float(line_raw))
        except ValueError:
            print("Value error converting line to float: ", line_raw)
            line = 0.0

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

    test_df = test_df.append(duke_dict, ignore_index=True)
    test_df = test_df.append(unc_dict, ignore_index=True)

    #duke is the home team
    duke_stats = test_df[test_df["Team"] == "Duke"]
    duke = Team("Duke", duke_stats)

    unc_stats = test_df[test_df["Team"] == "UNC"]
    unc = Team("UNC", unc_stats)

    test_game = Game(duke, unc, 150.0, 5) #the total here is arbitrary 
    return [test_game]

if __name__ == "__main__":

    avg_adj_off = scrape_adjusted_off_avg()
    print(avg_adj_off)
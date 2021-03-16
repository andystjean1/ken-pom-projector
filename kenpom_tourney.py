import pandas as pd
from bs4 import BeautifulSoup
import requests


def scrape_ken_pom():
    url = "https://kenpom.com/index.php"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'html.parser')

    # find the table and header tags and store them in a list
    table = soup.find_all('table', {'id': 'ratings-table'})[0]
    headers = table.find('thead').find('tr', {'class': 'thead2'})
    cols = [th.text for th in headers.find_all('th')]

    kenpom_df = pd.DataFrame(columns=cols)

    # get the data elements from the table and process each row
    body = table.find_all('tbody')[0]
    rows = body.find_all('tr')

    for r in rows:
        data = r.find_all('td')
        info = []

        try:
            if("tourney" in r["class"]):

                for d in data:
                    try:
                        if(d["class"] != ['td-right']):
                                info.append(d.text)
                    except:
                        info.append(d.text)   

                if(info != []):
                        info_df = pd.Series(info, index=cols)
                        kenpom_df = kenpom_df.append(info_df, ignore_index=True) 
        except:
            pass

      

            
            

    # clean and convert columns
    # kenpom_df["Team"] = kenpom_df.apply(lambda row: format_state_names(row), axis=1)
    kenpom_df["AdjO"] = pd.to_numeric(kenpom_df["AdjO"])
    kenpom_df["AdjD"] = pd.to_numeric(kenpom_df["AdjD"])
    kenpom_df["AdjT"] = pd.to_numeric(kenpom_df["AdjT"])
    kenpom_df = kenpom_df.assign(Seed=lambda x: (x["Team"][0][-1:]))

    return kenpom_df


# %%
from kenpom_tourney import scrape_ken_pom
scrape_ken_pom()
# %%

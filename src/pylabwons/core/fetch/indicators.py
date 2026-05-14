from bs4 import BeautifulSoup
from datetime import datetime
from pandas import DataFrame
import requests, time
import pandas as pd



def baker_hughes_rig_count(*years, **kwargs) -> DataFrame:
    if not years:
        years = [datetime.now().year + n for n in range(-12, 1)]

    objs = []
    for year in years:
        response = requests.get(
            url=f"https://www.aogr.com/web-exclusives/us-rig-count/{year}",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 "
                              "Safari/537.36"
            },
            timeout=15,
            verify=kwargs.get('verify', True)
        )
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        divs = soup.find_all("div", class_="p-4 sm:table-row")

        data = []
        for div in divs:
            parts = list(div.stripped_strings)

            try:
                date = datetime.strptime(parts[0], "%m/%d/%Y").date()
            except (TypeError, ValueError, Exception):
                continue

            obj = {'date': date}
            key = []
            for part in parts[1:]:
                if part[0].isalpha():
                    if not part in obj:
                        obj[part] = ''
                        key.append(part)
                else:
                    if key:
                        obj[key[-1]] = part.split(' ')[-1].replace("(", "").replace(")", "")
            data.append(obj)

        df = pd.DataFrame(data).set_index('date').sort_index()
        cols = {c: c.split(" ")[0] for c in df.columns if not c.startswith("Ratio") and "(" in c}
        objs.append(df[cols.keys()].rename(columns=cols))

        time.sleep(0.5)

    df = pd.concat(objs, axis=0)
    for c in df.columns:
        df[c] = df[c].str.replace(",", "").str.replace(".", "").astype(int)
    df.index = pd.to_datetime(df.index)
    return df.sort_index()

if __name__ == "__main__":
    # df = baker_hughes_rig_count(2026)
    df = baker_hughes_rig_count()
    print(df)
    df.to_csv(r'C:\Users\Administrator\Downloads\rig_count.csv')
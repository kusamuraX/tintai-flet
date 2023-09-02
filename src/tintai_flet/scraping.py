from datetime import datetime, timedelta
import os
import urllib3
from bs4 import BeautifulSoup
import pandas as pd

urllib3.disable_warnings()
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}
http = urllib3.PoolManager()

df_col = ['name', 'address', 'rent', 'admin', 'menseki', 'floor', 'link']
condition_list = [
    "ar=030",
    "bs=040",
    "fw2=",
    "pc=30",
    "po1=16",
    "po2=99",
    "ta=13",
    "sc=13111",
    "oz=13111004",
    "oz=13111008",
    "oz=13111026",
    "oz=13111056",
    "cb=0.0",
    "ct=8.5",
    "et=9999999",
    "mb=20",
    "mt=9999999",
    "cn=30",
    "smk=r03",
    "co=1",
    "kz=1",
    "tc=0400101",
    "tc=0400301",
    "shkr1=03",
    "shkr2=03",
    "shkr3=03",
    "shkr4=03"]


def scraping_tintai_data() -> pd.DataFrame:
    condition = "&".join(condition_list)
    HTMLRES = http.request(
        "GET",
        f"https://suumo.jp/jj/chintai/ichiran/FR301FC001/?{condition}",
        headers=headers)
    SOUP = BeautifulSoup(HTMLRES.data, "html.parser")
    bukken_div = SOUP.find(id="js-bukkenList")
    bukken_ul_list = bukken_div.find_all("ul", class_="l-cassetteitem")
    bukken_data_list = []
    for bukken_ul in bukken_ul_list:
        bukken_li_list = bukken_ul.find_all("li")
        for bukken in bukken_li_list:
            if bukken.find(class_="cassetteitem_content-title"):
                bukken_data = []
                title = bukken.find(class_="cassetteitem_content-title").get_text(strip=True)
                address = bukken.find(class_="cassetteitem_detail-col1").get_text(strip=True)
                data_table = bukken.find("table", class_="cassetteitem_other")
                data_body_list = data_table.find_all("tbody")
                for data_body in data_body_list:
                    rent = data_body.find(class_="cassetteitem_price cassetteitem_price--rent").get_text(strip=True)
                    admin = data_body.find(class_="cassetteitem_price cassetteitem_price--administration").get_text(strip=True)
                    try:
                        menseki = data_body.find(class_="cassetteitem_menseki").get_text(strip=True)[:-2]
                        if float(menseki) < 22:  # 22m2以下は除外する
                            continue
                    except BaseException:
                        continue
                    floor = data_body.find_all("td")[2].get_text(strip=True)
                    link = "https://suumo.jp" + data_body.find("a", class_="js-cassette_link_href cassetteitem_other-linktext")['href']
                    bukken_data = [title, address, rent, admin, menseki, floor, link]
                    is_not_exsits = True
                    for appended in bukken_data_list:
                        if appended[1:5] == bukken_data[1:5]:
                            if "築" in appended[0] and "築" not in bukken_data[0]:
                                appended[0] = bukken_data[0]
                                appended[6] = bukken_data[6]
                            is_not_exsits = False
                            break
                    if is_not_exsits:
                        bukken_data_list.append(bukken_data)

    bukken_df = pd.DataFrame(data=bukken_data_list, columns=df_col)

    # データを保存する
    today = datetime.now()
    data_folder_path = os.getcwd() + "/data/" + today.strftime('%Y-%m-%d')
    if not os.path.exists(data_folder_path):
        os.makedirs(data_folder_path)
    bukken_df.to_json(data_folder_path + f"/bukken_{today.strftime('%H_%M')}.json")

    bukken_df = bukken_df.assign(is_new=False)

    yesterday = today + timedelta(days=-1)
    day_before_date_folder_path = os.getcwd() + "/data/" + yesterday.strftime('%Y-%m-%d')
    if os.path.exists(day_before_date_folder_path):
        day_before_files = os.listdir(day_before_date_folder_path)
        if len(day_before_files) > 0:
            day_before_df = pd.read_json(day_before_date_folder_path + "/" + day_before_files[0])
            for index, bukken in enumerate(bukken_df.itertuples()):
                is_new = True
                for day_before_bukken in day_before_df.itertuples():
                    if __is_match(bukken[2:6], day_before_bukken[2:6]):
                        is_new = False
                        break
                if is_new:
                    bukken_df.iloc[index, 7] = True
    # print(bukken_df)
    return bukken_df


def __is_match(list_1, list_2):
    assert len(list_1) == len(list_2), 'unmatched list size'
    is_match = True
    for i in range(len(list_1)):
        if str(list_1[i]) != str(list_2[i]):
            is_match = False
            break
    return is_match

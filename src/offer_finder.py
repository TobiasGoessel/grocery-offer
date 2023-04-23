import pandas as pd
from bs4 import BeautifulSoup
import re
import time
import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from glob import glob


def penny_from_web(url: str):
    # Creating and configuring options for selenium-browser
    options = Options()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument('log-level=3')

    # open Chrome Browser with options
    driver = Chrome(options=options)
    driver.get(url)

    # wait till first offer is loaded and scroll to the end to load everything
    for number in range(0, 50):
        number = number * 2000
        driver.execute_script(f"window.scrollTo(0, {number})")
        time.sleep(0.5)

    # parse html from selenium to BS4
    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup


def edeka_from_web(url: str):
    options = Options()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' \
                 '60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument('log-level=3')

    # open Chrome Browser with options
    driver = Chrome(options=options)
    driver.get(url)
    for number in range(0, 20):
        number = number * 2000
        driver.execute_script(f"window.scrollTo(0, {number})")
        time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    return soup


def penny_to_pandas(soup, cfg: dict):
    # date_week = soup.find("div", class_="category-menu__header-week active")
    current_date = soup.find("div", {"data-week": "current"})
    next_date = soup.find("div", {"data-week": "next"})
    current_date_format = current_date["data-startend"]
    next_date_format = next_date["data-startend"]
    # date_week = date_week["data-startend"]
    start_date_current = re.search("([0-9]{2}\.){2} -", current_date_format).group()
    start_date_current = datetime.datetime.strptime(start_date_current[:-2] + str(datetime.date.today().year
                                                                                  ), "%d.%m.%Y").date()
    end_date_current = re.search("- ([0-9]{2}\.){2}", current_date_format).group()
    end_date_current = datetime.datetime.strptime(end_date_current[2:] + str(
        datetime.date.today().year
    ), "%d.%m.%Y").date()

    try:
        start_date_next = re.search("([0-9]{2}\.){2} -", next_date_format).group()
        start_date_next = datetime.datetime.strptime(start_date_next[:-2] + str(datetime.date.today().year
                                                                                ), "%d.%m.%Y").date()
        end_date_next = re.search("- ([0-9]{2}\.){2}", next_date_format).group()
        end_date_next = datetime.datetime.strptime(end_date_next[2:] + str(
            datetime.date.today().year
        ), "%d.%m.%Y").date()
    except AttributeError as ae:
        if cfg["debug"]:
            print(f"next week not found {ae}")

    try:
        monday_offers = soup.find("div", id="ab-montag")
        thursday_offers = soup.find("div", id="ab-donnerstag")
        friday_offers = soup.find("div", id="ab-freitag")
    except Exception as e:
        monday_offers = ""
        thursday_offers = ""
        friday_offers = ""
        if cfg["debug"]:
            print(f"ab montag not found{e}")
    try:
        nextmonday_offers = soup.find("div", id="ab-naechsten-montag")
        nextthursday_offers = soup.find("div", id="ab-naechsten-donnerstag")
        nextfriday_offers = soup.find("div", id="ab-naechsten-freitag")
    except Exception as e:
        nextmonday_offers = ""
        nextthursday_offers = ""
        nextfriday_offers = ""
        if cfg["debug"]:
            print(f"ab nächsten montag nicht gefunden{e}")

    try:
        single_offers_monday = monday_offers.find_all("ul", class_="tile-list")
        single_offers_thursday = thursday_offers.find_all("ul", class_="tile-list")
        single_offers_friday = friday_offers.find_all("ul", class_="tile-list")
    except Exception as e:
        single_offers_monday = ""
        single_offers_thursday = ""
        single_offers_friday = ""
        if cfg["debug"]:
            print(f"ab montag nicht gefunden{e}")

    try:
        single_offers_nextmonday = nextmonday_offers.find_all("ul", class_="tile-list")
        single_offers_nextthursday = nextthursday_offers.find_all("ul", class_="tile-list")
        single_offers_nextfriday = nextfriday_offers.find_all("ul", class_="tile-list")
    except Exception as e:
        single_offers_nextmonday = ""
        single_offers_nextthursday = ""
        single_offers_nextfriday = ""
        if cfg["debug"]:
            print(f"ab montag nicht gefunden{e}")
    if not single_offers_nextmonday:
        offers_singledays = [{"Ab Montag": single_offers_monday}, {"Ab Donnerstag": single_offers_thursday},
                             {"Ab Freitag": single_offers_friday}]
    else:
        offers_singledays = [{"Ab Montag": single_offers_monday},
                             {"Ab Donnerstag": single_offers_thursday},
                             {"Ab Freitag": single_offers_friday},
                             {"Ab nächsten Montag": single_offers_nextmonday},
                             {"Ab nächsten Donnerstag": single_offers_nextthursday},
                             {"Ab nächsten Freitag": single_offers_nextfriday}]
    monday_df = pd.DataFrame()
    product_df = pd.DataFrame()
    for singleday_offer in offers_singledays:
        for key in singleday_offer.keys():
            pass
        for offer in singleday_offer[key]:
            single_highlightproducts_singledayoffer = offer.find_all("li", class_="tile-list__item--highlight")
            single_products_singledayoffer = offer.find_all("li", class_="tile-list__item")
            for single_product_dayoffer in single_products_singledayoffer:
                try:
                    price = single_product_dayoffer.find("span", class_="ellipsis bubble__price").text
                    article = single_product_dayoffer.find("a", class_="tile__link--cover").text
                    unit = single_product_dayoffer.find("div", class_="offer-tile__unit-price ellipsis").text
                    basic_price = ""
                    market = "Penny"
                    date = key
                    kw = start_date_current.isocalendar()[1]
                    year = start_date_current.isocalendar()[0]
                    data = {"Artikelbezeichnung": article, "Streichpreis": "old_price", "Preis": price,
                            "Einheit": unit, "Markt": market, "Startdatum": start_date_current,
                            "Enddatum": end_date_current, "Gültig ab": date, "KW": kw, "Jahr": year}
                    product_df = pd.DataFrame(data, index=[0])
                except AttributeError:
                    if cfg["debug"]:
                        print("Some Attributes ar missing")
                monday_df = pd.concat([monday_df, product_df], ignore_index=True)
                for single_highlightproduct_singledayoffer in single_highlightproducts_singledayoffer:
                    try:
                        price = single_highlightproduct_singledayoffer.find("span",
                                                                            class_="ellipsis bubble__price"
                                                                            ).text
                        article = single_highlightproduct_singledayoffer.find("a",
                                                                              class_="tile__link--cover"
                                                                              ).text
                        unit = single_highlightproduct_singledayoffer.find("div",
                                                                           class_="offer-tile__unit-price ellipsis"
                                                                           ).text
                        basic_price = ""
                        market = "Penny"
                        date = key
                        if "nächsten" in key:
                            print(key)
                        else:
                            pass
                        kw = start_date_current.isocalendar()[1]
                        year = start_date_current.isocalendar()[0]
                        data = {"Artikelbezeichnung": article, "Streichpreis": "old_price", "Preis": price,
                                "Einheit": unit, "Markt": market, "Startdatum": start_date_current,
                                "Enddatum": end_date_current, "Gültig ab": date, "KW": kw, "Jahr": year}
                        product_df = pd.DataFrame(data, index=[0])
                    except AttributeError:
                        if cfg["debug"]:
                            print("No Price found")
                    monday_df = pd.concat([monday_df, product_df], ignore_index=True)
    penny_df = monday_df
    penny_df["Preis"] = pd.to_numeric(penny_df["Preis"], errors='coerce')
    penny_df = penny_df.drop_duplicates()
    penny_df["Grundpreis"] = penny_df["Einheit"].str.extract(r"(1 [a-zA-Z]* = [0-9]*\.[0-9]{2})")
    penny_df["Grundpreis"] = penny_df["Grundpreis"].fillna(" = ")
    penny_df["Grundeinheit"] = penny_df["Grundpreis"].str.split("=")
    penny_df["Grundeinheit"] = penny_df["Grundeinheit"].apply(lambda x: [x][0][0])
    penny_df["Grundpreis"] = penny_df["Grundpreis"].str.split("=")
    penny_df["Grundpreis"] = penny_df["Grundpreis"].apply(lambda x: [x][0][1])
    penny_df["Grundpreis"] = penny_df["Grundpreis"].apply(lambda x: x.replace(".", ","))

    penny_df["Startdatum"].loc[penny_df["Gültig ab"].str.contains("nächst")] = start_date_current
    penny_df["Enddatum"].loc[penny_df["Gültig ab"].str.contains("nächst")] = end_date_current
    try:
        penny_df["Startdatum"].loc[~penny_df["Gültig ab"].str.contains("nächst")] = start_date_next
        penny_df["Enddatum"].loc[~penny_df["Gültig ab"].str.contains("nächst")] = end_date_next
    except UnboundLocalError as ule:
        if cfg["debug"]:
            print(f"No next week date found. Error: {ule}")
    """if pd.read_csv(f"..\\data\\{start_date_current}-penny_next_monday.csv"):
        if debug:
            print("Penny Angebot already exists")
    else:"""
    penny_df.to_csv(f"..\\data\\grocery_offers\\{start_date_current}-penny_wochenangebote.csv",
                    decimal=",", sep=";", encoding="UTF-8-sig", index=False)


def edeka_to_pandas(soup, cfg: dict):
    offers = soup.find_all("div", class_="css-10didr4")
    date_week = soup.find("span", class_="css-1skty0g").text
    start_date = re.search("vom ([0-9]{2}\.){2}[0-9]{4}", date_week).group()
    start_date = datetime.datetime.strptime(start_date[4:], "%d.%m.%Y").date()
    end_date = re.search("zum ([0-9]{2}\.){2}[0-9]{4}", date_week).group()
    end_date = datetime.datetime.strptime(end_date[4:], "%d.%m.%Y").date()
    offers_with_data = pd.DataFrame()
    for product_group in offers:
        product_group_offers = product_group.find_all("div", class_="has-size-s css-1olgk07")
        product_df = pd.DataFrame()
        for product_offer in product_group_offers:
            dataset = ["css-ws0zws", "css-6ha7pe"]
            for data in dataset:
                try:
                    articlename = product_offer.find("span", class_=data).text
                except AttributeError:
                    articlename = ""
                    if cfg["debug"]:
                        print(f"No Articlename found with css-{data}")
                if articlename:
                    break
                else:
                    pass
            try:
                price = product_offer.find("span", class_="css-1tty58m").text
            except AttributeError:
                price = ""
                if cfg["debug"]:
                    print("No Price Found")
            try:
                article_information = product_offer.find("p", class_="css-1muttx2").text
            except AttributeError:
                article_information = ""
                if cfg["debug"]:
                    print("No Price Found")
            market = "Edeka"
            date = "Ab Montag"
            kw = start_date.isocalendar()[1]
            year = start_date.isocalendar()[0]
            data = {"Artikelbezeichnung": articlename, "Streichpreis": "old_price", "Preis": price,
                    "Einheit": article_information, "Markt": market, "Startdatum": start_date, "Enddatum": end_date,
                    "Gültig ab": date, "KW": kw, "Jahr": year}
            product_df = pd.DataFrame(data, index=[0])
            offers_with_data = pd.concat([offers_with_data, product_df], ignore_index=True)
    edeka_df = offers_with_data.drop_duplicates()
    edeka_df["Grundpreis"] = edeka_df["Einheit"].str.extract(r"(1 [a-zA-Z]* = [0-9]*\,[0-9]{2})")
    edeka_df["Grundpreis"] = edeka_df["Grundpreis"].fillna(" = ")
    edeka_df["Grundeinheit"] = edeka_df["Grundpreis"].str.split("=")
    edeka_df["Grundeinheit"] = edeka_df["Grundeinheit"].apply(lambda x: [x][0][0])
    edeka_df["Grundpreis"] = edeka_df["Grundpreis"].str.split("=")
    edeka_df["Grundpreis"] = edeka_df["Grundpreis"].apply(lambda x: [x][0][1])
    edeka_df["Grundpreis"] = edeka_df["Grundpreis"].apply(lambda x: x.replace(".", ","))
    """if Path(f"..\\data\\{start_date}-edeka_wochenangebote.csv").isfile():
        if debug:
            print("Edeka Angebot already exists")
    else:"""
    offers_with_data.to_csv(f"..\\data\\grocery_offers\\{start_date}-edeka_wochenangebote.csv",
                            decimal=",", sep=";", encoding="UTF-8-sig", index=False)


def offers_reader(cfg: dict):
    concated_offers = pd.DataFrame()
    for file in glob(cfg["data_path"]+"\\grocery_offers\\*.csv"):
        offers = pd.read_csv(file, encoding="UTF-8-sig", decimal=",", sep=";")
        concated_offers = pd.concat([offers, concated_offers])

    return concated_offers


def data_downloader(cfg: dict):
    """

    :param cfg:
    :return:
    """
    try:
        offers_penny = penny_from_web(url=cfg["penny_path"])
        penny_to_pandas(soup=offers_penny, cfg=cfg)
    except TimeoutException as te:
        if cfg["debug"]:
            print(te)
    try:
        offers_edeka = edeka_from_web(url=cfg["edeka_path"])
        edeka_to_pandas(soup=offers_edeka, cfg=cfg)
    except Exception as e:
        if cfg["debug"]:
            print(e)


def standard_shopping_list_weekly(cfg: dict):
    """
    This function reads the standard_einkauf.csv and returns it.
    :param cfg:
    :return:
    """
    standard_einkauf = pd.read_csv(cfg["standardeinkauf_path"], encoding="UTF-8-sig", decimal=",", sep=";")
    standard_einkauf = standard_einkauf[["Artikelbezeichnung", "Preis", "Einheit", "Markt"]]
    return standard_einkauf


def reader(cfg: dict):
    """
    This function reads the standar_deinkauf.csv file from cfg-file and all the .csv files from the data_path to check
    if there are matching strings inside the offers from each grocery store. If there are matching strings
    it will write a csv file and return the offerslist dataframe.

    :param cfg:
    :return offerslist:
    """
    standardlist = standard_shopping_list_weekly(cfg=cfg)
    offerslist = pd.DataFrame()
    folder = glob(cfg["data_path"] + "\\grocery_offers\\*.csv")
    for path in folder:
        try:
            if path.strip() == cfg["standardeinkauf_path"].strip():
                pass
            else:
                offers = offers_reader(cfg=cfg)
        except pd.errors.EmptyDataError as e:
            offers = pd.DataFrame()
            if cfg["debug"]:
                print(e)

        offerslist = pd.concat([offerslist, offers], ignore_index=True)
    buyinglist = pd.DataFrame()
    standardlist = standardlist.fillna(value="")
    offerslist = offerslist.fillna(value="")
    for articlename in standardlist["Artikelbezeichnung"]:
        splitted_articlenames = articlename.split(" ")
        for splitted_article in splitted_articlenames:
            offer_search = offerslist.loc[offerslist["Artikelbezeichnung"].str.contains(splitted_article)]
            if offer_search.empty:
                pass
            else:
                buyinglist = pd.concat([buyinglist, offerslist.loc[
                    offerslist["Artikelbezeichnung"].str.contains(splitted_article)]
                                        ])

    offerslist = buyinglist.drop_duplicates()
    offerslist.to_csv(f"..\\data\\{str(datetime.date.today())}-einkaufsliste.csv",
                       decimal=",", sep=";", encoding="UTF-8-sig", index=False)
    return offerslist


if __name__ == "__main__":
    penny_link = ""
    penny_to_pandas(penny_from_web(penny_link))

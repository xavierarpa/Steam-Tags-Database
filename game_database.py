"""
Author: Zach Morgan
Description: Creates a database of games and their tags
"""

import requests
from bs4 import BeautifulSoup
import time
import math
import sqlite3


def find_total_pages(filter):
    
    """
    Parameters: String filter - indicating which filter to be used for the search page, Example: Games only = 'category1=998'
    Purpose: Retrieve the total amount of pages of games from the search page
    Returns: Integer page count
    """
    
    first_page = requests.get("https://store.steampowered.com/search/?" + filter, timeout=30)
    html = BeautifulSoup(first_page.content, "html.parser")
    div = html.find("div", class_="search_pagination_left")
    if div is None:
        print("Warning: Could not find pagination element, defaulting to 1 page")
        return 1
    split = div.contents[0].split()
    # Expected format: "showing X - Y of Z"
    if len(split) >= 6:
        total_pages = math.ceil(int(split[5]) / 25)
    else:
        print(f"Warning: Unexpected pagination format: {split}, defaulting to 1 page")
        return 1
    print(f"Found {total_pages} pages to process")
    return total_pages


def get_tags(page):
    
    """
    Parameters: Request object page
    Purpose: Aquire a tuple of the title and a list of the tags
    Returns: Tuple (String, List)
    """

    html = BeautifulSoup(page.content, "html.parser")
    title_element = html.find("title")
    if title_element is None or len(title_element.contents) == 0:
        return "", ""
    
    title_raw = title_element.contents
    trim = title_raw[0].split()
    on_steam = False
    save = False
    title = ""
    
    if len(trim) >= 2 and " ".join(trim[-2:]) == "on Steam":
        on_steam = True
    if len(trim) > 1 and "%" in trim[1]:
        save = True
    if on_steam and not save:
        title = " ".join(trim[0:-2])
    if save and not on_steam:
        title = " ".join(trim[2:])
    if save and on_steam:
        title = " ".join(trim[3:-2])
    if not save and not on_steam:
        title = str(title_raw[0]) if title_raw else ""        
    tags_raw = html.find_all("a", class_="app_tag")
    tags_list = []
    for tag_element in tags_raw:
        if tag_element.contents and len(tag_element.contents) > 0:
            tag = tag_element.contents[0].strip()
            if tag:
                tags_list.append(tag)
    formatted_tags = ",".join(tags_list[:])
    return title, formatted_tags               
    

def create_database_list(c, tablename):
    
    """
    Parameters: Sqlite3 object c - connection to database, String tablename - name of table to create list from
    Purpose: Creates a list of all the ID's in the table
    Returns: List
    """

    c.execute("SELECT * FROM " + tablename)
    all_games = c.fetchall()
    game_lst =[]
    for game in all_games:
        game_lst.append(game[0])
    return game_lst


def find_duplicates(game_lst):
    """
    Purpose: Create a list of duplicates in the database
    Doesn't really work 100%, website still functions without it, if working would save a little bit of space in the db file but thats about it
    """
    seen = set()
    duplicates = set()
    for game in game_lst:
        if game not in seen:
            seen.add(game)
        else:
            duplicates.add(game)
    return duplicates


def maintain_database(conn, total_pages, tablename, filter):
    
    """
    Parameters: conn - database connection 
    Integer total_pages - total page number aquired from the find_total_pages function
    String tablename - name of the table to perform maintainance on
    String filter - indicating which filter to be used for the search page, Example: Games only = 'category1=998'

    Purpose: Performs maintaince on an existing table, or creates one
    
    Returns: NONE
    """

    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS " + tablename + "(id TEXT, title TEXT, tags TEXT)")
    page_count = 0
    games_on_steam = {}
    maintain = True
    #Checks whether a table exists already, if it does it leaves the maintain value True
    try:
        c.execute("SELECT * FROM " + tablename)
    except:
        maintain = False
    #Pages in the steam store start at 1, not 0
    total_games_added = 0
    for page_number in range(1, total_pages + 1):
        page_count += 1
        try:
            # Build the search URL with proper query string
            url = "https://store.steampowered.com/search/?" + filter + "&page=" + str(page_number)
            page = requests.get(url, timeout=30)
            html = BeautifulSoup(page.content, "html.parser")
            # Find all search result rows (anchor elements with search_result_row class)
            search_results = html.find_all("a", class_="search_result_row")
            links_lst = []
            #creates a list of the Store URLs on the current search page
            for result in search_results:
                href = result.get("href")
                if href:
                    links_lst.append(href)
            #Cookies that by pass the age gate for age restricted games
            agecheck = {'birthtime': '568022401'}
            for link in links_lst:
                try:
                    id_lst = link.split("/")
                    # App ID is typically at index 4: https://store.steampowered.com/app/APPID/...
                    if len(id_lst) > 4:
                        id = id_lst[4]
                    else:
                        continue
                    #check if game is new and not in database yet
                    c.execute("SELECT title FROM " + tablename + " WHERE id=?", (str(id),))
                    data = c.fetchone()
                    if data is None:
                        game_page = requests.get(link, cookies=agecheck, timeout=30)
                        title, tags = get_tags(game_page)
                        c.execute("INSERT INTO " + tablename + " VALUES(?, ?, ?)", (id, title, tags))
                        total_games_added += 1
                    games_on_steam[id] = None
                except Exception as e:
                    print(f"Error processing game link {link}: {e}")
            conn.commit()
            # Print progress every 10 pages
            if page_count % 10 == 0:
                print(f"Processed {page_count}/{total_pages} pages, added {total_games_added} games so far")
        except Exception as e:
            print(f"Error processing page {page_count}: {e}")
    print(f"Finished processing {page_count} pages, total games added: {total_games_added}")
    # Note: Maintenance code to delete old games commented out as it was causing issues
    # if maintain:
    #     game_lst = create_database_list(c, tablename)      
    #     for game in game_lst:
    #         if game not in games_on_steam:
    #             c.execute("DELETE FROM " + tablename + " WHERE id=?", [game])

def main():
    conn = sqlite3.connect("tags_database.db")
    c = conn.cursor()
    total_pages = find_total_pages("category1=998")
    maintain_database(conn, total_pages, "games_filter", "category1=998")
    conn.commit()
    c.close()


if __name__ == "__main__":
    main()


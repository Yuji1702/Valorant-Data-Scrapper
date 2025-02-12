import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from typing import List, Dict
import logging
import csv
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

class ValorantDataCollector:
    def __init__(self):
        self.base_url = "https://www.vlr.gg"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_player(self, player_name: str) -> str:
        """Search for a player by name and return their profile URL, filtering for players"""
        search_url = f"{self.base_url}/search/?q={player_name.replace(' ', '%20')}&type=players"
        response = requests.get(search_url, headers=self.headers)
        
        logging.info(f"Request URL: {response.url}")
        logging.info(f"Response status: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"Failed to retrieve search page for {player_name}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info(f"Page content: {soup.prettify()[:1000]}")

        try:
            player_link = soup.find('a', class_='search-item')

            if player_link:
                profile_url = self.base_url + player_link['href']
                logging.info(f"Found player profile: {profile_url}")
                return profile_url
            else:
                logging.warning(f"Player {player_name} not found in the 'players' category.")
                return None
        except Exception as e:
            logging.error(f"Error parsing search results: {e}")
            return None

    def get_player_stats(self, url: str) -> Dict:
        """Extract stats for a single player"""
        url_with_timespan = f"{url}?timespan=all"
        response = requests.get(url_with_timespan, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        name_tag = soup.find('h1', class_='wf-title')
        name = name_tag.text.strip() if name_tag else 'Unknown'

        stats_table = soup.find('table', class_='wf-table')
        stats = []

        if stats_table:
            try:
                stats_rows = stats_table.find('tbody').find_all('tr')
                for row in stats_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        agent_img = cells[0].find('img')
                        agent_name = agent_img['alt'] if agent_img else 'Unknown'

                        usage = cells[1].text.strip()
                        rounds_played = cells[2].text.strip()
                        rating = cells[3].text.strip()
                        acs = cells[4].text.strip()
                        kd = cells[5].text.strip()
                        adr = cells[6].text.strip()
                        kast = cells[7].text.strip()
                        kpr = cells[8].text.strip()
                        apr = cells[9].text.strip()
                        fkpr = cells[10].text.strip()
                        fdpr = cells[11].text.strip()
                        kills = cells[12].text.strip()
                        deaths = cells[13].text.strip()
                        assists = cells[14].text.strip()
                        first_kills = cells[15].text.strip()
                        first_deaths = cells[16].text.strip()

                        stats.append({
                            'Agent': agent_name,
                            'Usage': usage,
                            'Rounds Played': rounds_played,
                            'Rating': rating,
                            'ACS': acs,
                            'K:D': kd,
                            'ADR': adr,
                            'KAST': kast,
                            'KPR': kpr,
                            'APR': apr,
                            'First Kills Per Round': fkpr,
                            'First Deaths Per Round': fdpr,
                            'Kills': kills,
                            'Deaths': deaths,
                            'Assists': assists,
                            'First Kills': first_kills,
                            'First Deaths': first_deaths
                        })

                return {
                    'Name': name,
                    'Stats': stats
                }

            except Exception as e:
                logging.error(f"Error processing player {name}: {str(e)}")
                return None
        else:
            logging.warning(f"Stats table not found for player: {name}")
            return None


def export_player_stats_to_csv(player_data, filename='all_players_stats.csv'):
    """Exports player stats to a single CSV file with a row for each agent."""
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Writing headers only once if the file is being created
        if file.tell() == 0:
            writer.writerow([
                'Name', 'Agent', 'Usage', 'Rounds Played', 'Rating', 'ACS', 'K:D',
                'ADR', 'KAST', 'KPR', 'APR', 'First Kills Per Round', 'First Deaths Per Round',
                'Kills', 'Deaths', 'Assists', 'First Kills', 'First Deaths'
            ])

        for stat in player_data['Stats']:
            writer.writerow([
                player_data['Name'],
                stat['Agent'],
                stat['Usage'],
                stat['Rounds Played'],
                stat['Rating'],
                stat['ACS'],
                stat['K:D'],
                stat['ADR'],
                stat['KAST'],
                stat['KPR'],
                stat['APR'],
                stat['First Kills Per Round'],
                stat['First Deaths Per Round'],
                stat['Kills'],
                stat['Deaths'],
                stat['Assists'],
                stat['First Kills'],
                stat['First Deaths']
            ])

def collect_data_for_player(player_name, collector):
    """Collect data for a single player and save it."""
    player_url = collector.search_player(player_name)
    if player_url:
        player_stats = collector.get_player_stats(player_url)
        if player_stats:
            export_player_stats_to_csv(player_stats)

def collect_and_save_data(player_names: List[str], concurrent=False):
    """Collect data for specified players and save to CSV."""
    collector = ValorantDataCollector()
    
    logging.info(f"Collecting data for {len(player_names)} players...")
    
    if concurrent:
        # Use concurrent requests for faster scraping
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(collect_data_for_player, player_name, collector) for player_name in player_names]
            for future in futures:
                future.result()  # wait for all threads to finish
    else:
        # Sequential scraping
        for player_name in player_names:
            logging.info(f"Searching for player: {player_name}")
            collect_data_for_player(player_name, collector)
            time.sleep(random.uniform(1, 2))  # Respectful scraping

    logging.info(f"Data collection completed.")

if __name__ == "__main__":
    try:
        player_names = input("Enter the player names (comma-separated): ").split(',')
        player_names = [name.strip() for name in player_names]

        # Choose whether to use concurrent scraping
        concurrent = input("Do you want to scrape concurrently? (y/n): ").lower() == 'y'

        collect_and_save_data(player_names, concurrent=concurrent)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
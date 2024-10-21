# Valorant Data Collector

This Python project scrapes and collects Valorant player statistics from [VLR.gg](https://www.vlr.gg) using web scraping techniques. The data is exported to a CSV file for analysis, including detailed player performance data, such as agents used, rounds played, ACS, K/D ratio, and more.

## Features

- **Player Search**: Search for a Valorant player by name and retrieve their profile.
- **Data Extraction**: Extract detailed stats for each agent a player has used, including key performance metrics.
- **Multithreading Support**: Option to scrape player stats concurrently using multiple threads.
- **Data Export**: Export player stats to a CSV file for easy analysis.

## Technologies

- `requests`: For sending HTTP requests to retrieve data from the web.
- `BeautifulSoup`: For parsing and scraping the HTML content of web pages.
- `pandas`: For data manipulation and export (optional).
- `csv`: To export the player stats into a CSV format.
- `logging`: For detailed logging of the scraping process.
- `ThreadPoolExecutor`: For concurrent scraping to speed up data collection.

## Installation

To use this project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/your-username/valorant-data-collector.git
cd valorant-data-collector
pip install -r requirements.txt

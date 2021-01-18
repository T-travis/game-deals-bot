from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup, Tag, ResultSet
from typing import List, Any

from game_sale import GameSale
from game_match import GameMatch

from pathlib import Path
from dotenv import load_dotenv
import os


class GameScraper:
    """
    GameBot scrapes isthereanydeal.com for games and prices/sales.

    """

    def __init__(self):
        # setup chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
        # get URL from env and navigate to link
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        self.is_there_any_deal_url = os.getenv('URL')  # base url for searching games
        self.selected_game_url = ''  # url of game to set reminders for sales
        self.driver.get(self.is_there_any_deal_url)
        # set default values
        self.timeout = 5
        self.games = []
        self.sales = []
        self.error_message = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """clean up method"""
        self.driver.quit()

    def error_handler(self, arr):
        """Checks soup results passed from this that are usually None or [] if not found passed 
        
        Parameters:
        arr (list): list of soup objects 

        """

        if type(arr) != list or not arr:
            self._error("Search not found or contains no game data. Please try again or try another search.")

        for obj in arr:
            if not obj:
                self._error("Search not found or contains no game data. Please try again or try another search.")

    async def game_search(self, user_input):
        """Sets possible matches in self.games.

        Parameters:
        user_input (str): search input from a discord user

        """

        try:
            # find search box on page
            search_box = WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located((By.ID, "searchbox")))
            # enter user input into search box
            ActionChains(self.driver).send_keys_to_element(search_box, user_input).perform()
            # perform search of input
            ActionChains(self.driver).send_keys_to_element(search_box, Keys.ENTER).perform()
            # create data object to send back (name, image, link ref for future searches)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            self.error_handler([soup])
            card_container = soup.find_all('div', class_='card-container')
            self.error_handler([card_container])

            for card in card_container:
                if card:

                    # skip matches with no good game data
                    no_data = card.find('span', text='Current Best:')
                    if not no_data:
                        continue

                    game_anchor = card.find('a', class_='card__title')
                    self.error_handler([game_anchor])
                    
                    game_title = game_anchor.text
                    game_href = game_anchor['href']
                    self.games.append(GameMatch(game_href, game_title))

            self.error_message = ''
        except AttributeError:
            self._error("Search not found. Please try again or try another search.")
        except KeyError:
            self._error("Missing attribute error! Please try again or try another search.")
        except TimeoutException:
            self._error("Search not found. Please try again or try another search.")
        except NoSuchElementException:
            self._error("Search not found. Please try another search.")

    async def get_game(self, game_href):
        """Returns a list of sale info for a single game.

        Parameters:
        game_href (str): partial link from a prior search using game_search

        """
        try:
            self.selected_game_url = self.is_there_any_deal_url + game_href
            self.driver.get(self.selected_game_url)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            self.error_handler([soup])

            game_title_h1 = soup.find('h1', {'id':'gameTitle'})
            sales_table = soup.find('div', class_='table-container')

            no_data = sales_table.find('div', class_='widget__nodata')
            if no_data:
                self.error_message = 'This game contains no data.'
                return

            self.error_handler([sales_table])
            sales_info = sales_table.find_all('tr')
            self.error_handler([game_title_h1, sales_table, sales_info])

            game_title = game_title_h1.text
            self.error_handler([game_title])

            sales_info = sales_info[1:-1]

            self.error_handler([sales_info])

            for sale in sales_info:
                company_obj = sale.find('a', class_='shopTitle')
                platforms_obj = sale.find('td', class_='priceTable__platforms')
                current_sale_percent_obj = sale.find('td', class_='priceTable__cut')
                current_sale_price_obj = sale.find('td', class_='priceTable__new')
                lowest_historical_price_obj = sale.find('td', class_='priceTable__low')
                base_price_obj = sale.find('td', class_='priceTable__old')
                game_sale_link_obj = sale.find('a', class_='shopTitle')
                self.error_handler([company_obj, platforms_obj, current_sale_percent_obj, current_sale_price_obj, \
                lowest_historical_price_obj, base_price_obj, game_sale_link_obj])

                company = company_obj.text
                platforms = platforms_obj.text
                current_sale_percent = current_sale_percent_obj.text
                current_sale_price = current_sale_price_obj.text
                lowest_historical_price = lowest_historical_price_obj.text
                base_price = base_price_obj.text
                game_sale_link = game_sale_link_obj['href']
                self.error_handler([company, platforms, current_sale_percent, current_sale_price, \
                lowest_historical_price, base_price, game_sale_link])
                
                game_sale = GameSale(game_title, company, platforms, current_sale_percent, current_sale_price, lowest_historical_price, base_price, game_sale_link)
                self.sales.append(game_sale)

            self.error_message = ''
        except AttributeError:
            self._error("Search not found. Please try again or try another search.")
        except KeyError:
            self._error("Missing attribute error! Please try again or try another search.")
        except TimeoutException:
            self._error("Search not found. Please try again or try another search.")
        except NoSuchElementException:
            self._error("Search not found. Please try another search.")

    def _error(self, message):
        """Handles errors caught from try/except blocks"""

        self.error_message = message
        self.driver.quit()
        return

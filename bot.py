from pathlib import Path
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord import Embed
import discord
import os
import time

from game_scraper import GameScraper
from input_validator import InputValidator


class GameBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.validator = InputValidator()

    @commands.command(name='test')
    async def test(self, ctx):
        """Used for testing the bot is running."""
        await ctx.send('the server is ready for action...')

    @commands.command(name='search')
    async def game_search(self, ctx, *, arg):
        """Search for a game by its name and send games info to the caller.
        
        Parameters:
        arg (str): the name of a video game

        """

        if not self.validator.valid_search_input(arg):
            await ctx.send("Please enter a valid game name")
            return

        await self._game_search(ctx, arg)

    async def _game_search(self, ctx, arg):

        with GameScraper() as scraper:
            await scraper.game_search(arg)
            if scraper.error_message:
                await ctx.send(f'{scraper.error_message}')
            else:
                if len(scraper.games) == 0:
                    await ctx.send('No matches found. Please try another search.')
                for game in scraper.games:
                    embed = Embed(title=f'{game.title}', color=0x00ff00)
                    embed.add_field(name="Search Command (use the command below to search for this game's info)", value=f'$game {game.href}', inline=True)
                    await ctx.send(embed=embed)

    @commands.command(name='game')
    async def get_game(self, ctx, *, arg):
        """Sends game info to the caller.
        
        Parameters:
        arg (str): partial link from a prior search using game_search()

        """
        
        if not self.validator.valid_game_url_input(arg):
            await ctx.send("Please enter a valid game search url")
            return

        await self._get_game(ctx, arg)

    async def _get_game(self, ctx, arg):

        with GameScraper() as scraper:
            await scraper.get_game(arg)
            if scraper.error_message:
                await ctx.send(f'{scraper.error_message}')
            else:
                if len(scraper.sales) == 0:
                    await ctx.send('Search not found')
                else:
                    for sale in scraper.sales:
                        embed = await self._game_embed(sale)
                        await ctx.send(embed=embed)

    async def _game_embed(self, sale):

        embed = Embed(title=f'{sale.game_title}', color=0x00ff00)
        embed.add_field(name='Company', value=f'{sale.company}', inline=True)
        embed.add_field(name='Platforms', value=f'{sale.platforms}', inline=True)
        embed.add_field(name='Base Price', value=f'{sale.base_price}', inline=True)
        embed.add_field(name='Current Sale Percent', value=f'{sale.current_sale_percent}', inline=True)
        embed.add_field(name='Current Sale Price', value=f'{sale.current_sale_price}', inline=True)
        embed.add_field(name='Historical Low Price', value=f'{sale.lowest_historical_price}', inline=True)
        embed.add_field(name='Game Sale Link ', value=f'{sale.game_sale_link}', inline=False)

        return embed


def main():
    env_path: Path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    bot_token = os.getenv('DISCORD_TOKEN')
    bot = commands.Bot(command_prefix='$')
    bot.add_cog(GameBot(bot))
    bot.run(bot_token)


if __name__ == '__main__':
    main()

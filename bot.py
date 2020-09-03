from os import path
import json
import discord
import sys
import asyncio
from pyquery import PyQuery as pq
from urllib import request

data = {
    'nintendolife': {},
    'pokecommunity': {}
}

config = {
    'token': '',
    'newsChannelID': ''
}

def saveData():
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.close()

if not path.isfile('data.json'):
    saveData()
else:
    with open('data.json', 'r') as f:
        data = json.load(f)
        f.close()

if not path.isfile('config.json'):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
        f.close()
else:
    with open('config.json', 'r') as f:
        config = json.load(f)
        f.close()

def getLatestNews(website):
    if 'nintendolife' in website:
        req = request.urlopen("https://www.nintendolife.com/pokemon/news")
        html = req.read().decode('utf8')
        req.close()
        q = pq(html)
        nintendolife_latest = pq(q('a[class*="title accent-hover"]').html())
        cat = nintendolife_latest('span[class*="category"]').html()
        news = nintendolife_latest('span[class*="title"]').html()
        path = q('a[class*="title accent-hover"]').attr('href')
        link = 'https://www.nintendolife.com/' + path
        imglink = pq(q(f'a[href*="{path}"]').html())('img').attr('src')
        description = pq(q(f'li[data-subject*="{path}"]').html())('p[class="description"]').html()
        return {'title': f'{cat} | {news}', 'description': description, 'imglink': imglink, 'link': link}
    if 'pokecommunity' in website:
        req = request.urlopen("https://daily.pokecommunity.com/category/news/")
        html = req.read().decode('utf8')
        req.close()
        q = pq(pq(html)('article:nth-of-type(1)').html())
        news = q('h1[class="entry-title"]').text()
        cat = q('span[class="cat-links"]').text()
        link = pq(q('h1[class="entry-title"]').html())('a').attr('href')
        imglink = q('img').attr('src')
        description = q('div[class="entry-summary"]').text()
        return {'title': f'{cat} | {news}', 'description': description, 'imglink': imglink, 'link': link}
    return {'title': '', 'description': '', 'imglink': '', 'link': ''}

if config.get('token') == '':
    print('Bot token not passed. A valid bot token should be passed in order for this to work.')
    print('The process will now exit.')
    sys.exit()

if config.get('newsChannelID') == '':
    print('News channel ID not passed. A valid channel ID should be passed in order for this to work.')
    print('The process will now exit.')
    sys.exit()

async def newsProcess():
    while True:
        channel = bot.get_channel(int(config.get('newsChannelID')))
        if channel is None:
            print('News channel ID is not valid.')
            return
        news = getLatestNews('nintendolife')
        if data.get('nintendolife') != news:
            print('Got a news from Nintendo Life, Posting.')
            embed = discord.Embed(title=news.get('title'), url=news.get('link'), description=news.get('description'), color=0xFFDE00)
            embed.set_image(url=news.get('imglink'))
            embed.set_author(name='Nintendo Life', url='https://www.nintendolife.com/')
            await channel.send(embed=embed)
            data['nintendolife'] = news
            saveData()
        news = getLatestNews('pokecommunity')
        if data.get('pokecommunity') != news:
            print('Got a news from PokeCommunity, Posting.')
            embed = discord.Embed(title=news.get('title'), url=news.get('link'), description=news.get('description'), color=0xFFDE00)
            embed.set_image(url=news.get('imglink'))
            embed.set_author(name='PokéCommunity Daily', url='https://daily.pokecommunity.com/')
            await channel.send(embed=embed)
            data['pokecommunity'] = news
            saveData()
        await asyncio.sleep(5)

class DiscordClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await newsProcess()

bot = DiscordClient()

bot.run(config.get('token'))
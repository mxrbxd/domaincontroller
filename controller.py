import discord
import requests
import asyncio
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

TOKEN = "token" # bot tokeninizi girin buraya 
CHANNEL_ID = 1 #kontrolün olacağı kanalın id si
USOM_URL = "https://www.usom.gov.tr/adres"
CHECK_INTERVAL = 5  

target_domains = {"terorlemucadele.net"}  
alert_active = False  
isolated_users = set()  

intents = discord.Intents.default()
intents.messages = True    
bot = commands.Bot(command_prefix="!", intents=intents)

def get_usom_domains():
    url = "https://www.usom.gov.tr/url-list.txt" 
    response = requests.get(url)
    if response.status_code == 200:
        domain_list = set(response.text.splitlines()) 
        return domain_list
    return set()

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_usom():
    """USOM listesini belirli aralıklarla kontrol eder ve uyarı gönderir."""
    global alert_active
    if alert_active:
        return  
    
    usom_domains = get_usom_domains()
    print("USOM'dan çekilen domainler:", usom_domains)  
    matched_domains = target_domains.intersection(usom_domains)
    channel = bot.get_channel(CHANNEL_ID)
    if channel and matched_domains:
        alert_active = True  
        while alert_active:
            message = "@everyone ⚠️ DOMAİNİNİZ USOM'A YAKALANDI: \n" + "\n".join(matched_domains)
            await channel.send(message)
            await asyncio.sleep(3) 

@bot.event
async def on_message(message):
    global alert_active
    if message.channel.id == CHANNEL_ID and message.content.lower() == "izole":
        alert_active = False  
        check_usom.cancel() 
        await message.channel.send(f"{message.author.mention} DURUM KONTROLÜNÜZ ALTINDA, DOMAİNİNİZİ DEĞİŞTİRİN")
    await bot.process_commands(message)  

@bot.event
async def on_ready():
    print(f"Bot {bot.user} olarak giriş yaptı.")
    check_usom.start()  

bot.run(TOKEN)
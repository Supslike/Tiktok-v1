# main imports
import os
import re
import sys
import time
import discord
import asyncio
from replit import db
from utility import tiktok_downloader as tt
from utility import keep_alive as idle
from discord.ext import commands

# discord client
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "t!", help_command=None,intents=intents,activity=discord.Activity(type=discord.ActivityType.watching, name="Tiktok!"), status=discord.Status.idle)

# Tiktok downloader
tiktok = tt.TikTok()
db["running"] = False

global queue, current_queue
queue = {}
current_queue = None

@bot.command()
async def restart(ctx):
  if ctx.author.id == await bot.application_info().owner.id:
    await ctx.send("Restating...")
    await ctx.delete()
    os.system("kill 1")
    os.execv(sys.executable, ['python'] + sys.argv)
    
@bot.event
async def on_ready():
  print("READY TO DOWNLOAD")

def done(number):
  global queue, current_queue
  try:
    current_queue = queue[str(number + 1)]
  except KeyError:
    try:
      current_queue = queue[str(number + 2)]
    except KeyError:
      queue = {}
      current_queue = None
    except TypeError:
      queue = {}
      current_queue = None
  except TypeError:
    try:
      current_queue = queue[str(number + 2)]
    except KeyError:
      queue = {}
      current_queue = None
    except TypeError:
      queue = {}
      current_queue = None
  try:
    os.remove('./tt/video.mp4')
  except FileNotFoundError:
    pass
  db["running"] = False
  

# Tiktok downloader command
@bot.command()
async def download(ctx, name):
  global current_queue, queue
  is_running = db["running"]
  emoji = bot.get_emoji(946741706122997780)
  await ctx.message.add_reaction(emoji)
  number = len(queue)
  if is_running:
    queue[str(number + 1)] = name
    while is_running:
      if current_queue == name:
        del queue[str(number + 1)]
        break
  db["running"] = True
  start_time = time.time()
  url = tiktok.download_video(name)
  await ctx.message.remove_reaction(emoji, bot.user)
  if url == None:
    await ctx.reply("Sorry something went wrong!, I tried many times")
    done(number)
    return
  if url == False:
    await ctx.reply("Invalid link provided")
    done(number)      
    return
  if os.path.getsize("./tt/video.mp4") == 0:
    await ctx.reply("Sorry something went wrong internally in this video, This is a bug from tiktok")
    await ctx.message.add_reaction("❌")
    done(number)
    return
  file = discord.File("./tt/video.mp4")
  try:
    try:
      await ctx.reply(content=f"||Took {int(time.time() - start_time)} seconds||",file=file)
    except:
        file = discord.File("./tt/video.mp4")
        await asyncio.sleep(2)
        await ctx.reply(content=f"||Took {int(time.time() - start_time)} seconds||",file=file)
  except discord.errors.HTTPException:
    try:
      await ctx.reply(f"||Took {int(time.time() - start_time)} seconds||\nFile too big to send but you can download the video in this link\n\n{url}")
    except:
        file = discord.File("./tt/video.mp4")
        await asyncio.sleep(2)
        await ctx.reply(f"||Took {int(time.time() - start_time)} seconds||\nFile too big to send but you can download the video in this link\n\n{url}")
  done(number)

# Tiktok detector
@bot.event
async def on_message(msg):
  global current_queue, queue
  is_running = db["running"]
  if f"download" in msg.content:
    await bot.process_commands(msg)
    return
  try:
    url = re.search("(?P<url>https?://[^\s]+)", str(msg.content)).group("url")
  except AttributeError:
    await bot.process_commands(msg)
    return
  if "tiktok" in url:
    emoji = bot.get_emoji(946741706122997780)
    await msg.add_reaction(emoji)
    number = len(queue)
    if is_running:
      queue[str(number + 1)] = url
      while is_running:
        if current_queue == url:
          del queue[str(number + 1)]
          break
        await asyncio.sleep(0.5)
    db["running"] = True
    start_time = time.time()
    url = tiktok.download_video(url)
    await msg.remove_reaction(emoji, bot.user)
    if url == None:
      print("something went wrong")
      await msg.add_reaction("❌")
      done(number)
      return
    if url == False:
      print("invalid link provided")
      await msg.add_reaction("❌")
      done(number)
      return
    if os.path.getsize("./tt/video.mp4") == 0:
      print("Sorry something went wrong internally in this video, This is a bug from tiktok")
      await msg.add_reaction("❌")
      done(number)
      return
    file = discord.File("./tt/video.mp4")
    try:
      try:
        await msg.channel.send(content=f"||Took {int(time.time() - start_time)} seconds||",file=file, reference=msg)
      except:
        file = discord.File("./tt/video.mp4")
        await msg.channel.send(content=f"||Took {int(time.time() - start_time)} seconds||",file=file, reference=msg)
    except discord.errors.HTTPException:
      try:
        await msg.channel.send(f"||Took {int(time.time() - start_time)} seconds||\nFile too big to send but you can download the video in this link\n\n{url}", reference=msg)
      except:
        file = discord.File("./tt/video.mp4")
        await msg.channel.send(content=f"||Took {int(time.time() - start_time)} seconds||",file=file, reference=msg)
    done(number)
        
# run setup
idle.keep_alive()
try:
  bot.run(os.getenv("TOKEN"))
except discord.HTTPException:
  os.system("kill 1")
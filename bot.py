import garageScript
from math import ceil, floor
from PIL import Image
from io import BytesIO
import numpy
import json
import aiohttp
import asyncio
from discord.ext import tasks, commands
import discord
with open('config.json') as f:
    data = json.load(f)
token = str(data["discordBotToken"])

async def compileGarage(username):
    profile = await garageScript.compileProfileAsync(username)

    width = 913 + 24
    height = 30 + (ceil(len(profile["data"]['garage']) / 30) * 291)
    with Image.new('RGBA', (width, height)) as img:

        # Pasting lots
        with Image.open('OtherImports\parking_spots_all.png') as lots:
            for i in range(ceil(len(profile["data"]['garage']) / 30)):
                img.paste(lots, (12, 15 + (291 * i)), lots)

        garage = numpy.reshape(profile["data"]['garage'], (ceil(len(profile["data"]['garage']) / 15), 15))
        for y, row in enumerate(garage):
            for x, id in enumerate(row):

                # Skipping blanks
                if not id:
                    continue

                # Looking for garage car in cars
                id = int(id)
                car_details = [c for c in profile["data"]['cars'] if c[0] == id and c[1] == 'owned']
                if not car_details:
                    continue

                car_details = car_details[0]
                car = await garageScript.compileCarAsync(id, car_details[2], 'small')
                with Image.open(car) as c:
                    width = c.size[1]
                    length = c.size[0]
                    with c.rotate(90 if y % 2 == 0 else -90, expand=True, resample=Image.NEAREST) as temp:
                        _x = 12 + ((x * 61) + (30 - floor(width / 2)))
                        _y = 20 + (48 - floor(length / 2)) + (y * 181 - (floor(y / 2) * 71))
                        img.paste(temp, (_x, _y))

                car.close()

        with BytesIO() as b:
            img.save("garage.png", 'PNG')
            b.seek(0)

async def carLink(username):
    url = await garageScript.carLink(username)
    return(str(url))

bot = commands.Bot(command_prefix=str(data["botPrefix"]), activity = discord.Game(name="$garage [username]"))

@bot.command()
async def garage(ctx, username):
    username = str(username)
    if(".com" in username):
        usernameList = username.split("/")
        username = usernameList[len(usernameList)-1]
    elif('@' in username):
        username = username.replace("@", "")
    try:
        await ctx.send("Compiling garage of " + username)
        async with ctx.typing():
            await compileGarage(username)
        await ctx.send(file = discord.File("garage.png"))
    except:
        await ctx.send("Error! Could not compile garage.")

@bot.command()
async def car(ctx, username):
    username = str(username)
    if(".com" in username):
        usernameList = username.split("/")
        username = usernameList[len(usernameList)-1]
    elif('@' in username):
        username = username.replace("@", "")
    try:
        link = await carLink(username)
        await ctx.send(link)
    except:
        await ctx.send("Could not send car! Please try again!")

@bot.command()
async def find(ctx,carName):
    carName = str(carName)
    try:
        carDict = garageScript.findCar(carName)
        if(len(carDict) <= 0):
            await ctx.send("I found no cars matching that name!")
            return
        for x in carDict:
            await ctx.send(f'__**{x}:**__ https://www.nitrotype.com/cars/{carDict[x]}_large_1.png')
    except:
        await ctx.send("Invalid car! Please try again.")

bot.run(token)

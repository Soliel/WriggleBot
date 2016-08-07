from discord.ext import commands
import discord

description = "A bot to begin Regul's reign of tyranny over the servers."

startup_extensions = ["Scripts.Cogs.Reversal", "Scripts.Cogs.PetClaim", "Scripts.Cogs.Meme", "Scripts.Cogs.PetBattle"]

bot = commands.Bot(command_prefix='t~', description = description)

@bot.event
async def on_ready():
	print("Logged in as ")
	print(bot.user.name)
	print(bot.user.id)
	print('-----------')
	
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			exc = '{}: {}'.format(type(e).__name__, e)
			print('failed to load extension {}\n{}'.format(extension,exc))


@bot.command()
async def load(extension_name : str):
	try:
		bot.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
		return
	await bot.say("{} loaded.".format(extension_name))


@bot.command()
async def unload(extension_name : str):
	bot.unload_extension(extension_name)
	await bot.say("{} unloaded.".format(extension_name))
	
	
@bot.command()
async def reload(extension_name : str):
	bot.unload_extension(extension_name)
	try:
		bot.load_extension(extension_name)
	except (AttributeError, ImportError) as e:
		await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
		return
	await bot.say('{} Reloaded.'.format(extension_name));


bot.run("token")
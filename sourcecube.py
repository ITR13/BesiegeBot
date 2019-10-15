import discord
import asyncio
import re
import traceback

import config
import commands
from tokens import DISCORD_TOKEN as TOKEN

import lifebuoy
import mundane
import karma
import f1984
import leisure
import wisdom
import ihavenomouth

try:
	with open("./god_users.txt") as f:
		GOD_USERS = f.read().splitlines()
except IOError:
	with open("./god_users.txt",'w') as f:
		GOD_USERS = []


DEFAULT = mundane.game_status_per_message
mundane.SAVE = [
	config.save,
	karma.save,
	wisdom.save,
]

back_log = []
LOG_CHANNEL = None

commands = [
	(
		lambda m: (
			m.channel.name == 'screenshots' or
			m.channel.name == 'inspirations'
		), 
		f1984.check_screenshot
	),

	# Admin only commands
	commands.register(
		'reload',
		mundane.reload,
		admin=True, leisure=False,
	),
	commands.register(
		'set_log',
		mundane.set_log_channel,
		admin=True, leisure=False,
	),
	commands.register(
		'add_leisure',
		commands.add_leisure_channel,
		admin=True, leisure=False,
	),
	commands.register(
		'delete_leisure',
		commands.delete_leisure_channel,
		admin=True, leisure=False,
	),
	commands.register(
		'add_prefix',
		commands.add_prefix,
		admin=True, leisure=False,
	),
	commands.register(
		'delete_prefix',
		commands.delete_prefix,
		admin=True, leisure=False,
	),
	commands.register(
		'error',
		mundane.do_raise_error,
		admin=True, leisure=False,
	),
	commands.register(
		'reset_karma',
		karma.reset_karma,
		admin=True, leisure=False,
	),
	commands.register(
		'force_save',
		lifebuoy.force_save,
		admin=True, leisure=False,
	),
	commands.register(
		'temp_ban',
		ihavenomouth.temp_ban,
		admin=True, leisure=False,
		delete=False,
	),
	commands.register(
		'tban',
		ihavenomouth.temp_ban,
		admin=True, leisure=False,
		delete=False,
	),
	commands.register(
		'temp_mute',
		ihavenomouth.temp_mute,
		admin=True, leisure=False,
		delete=False,
	),
	commands.register(
		'tmute',
		ihavenomouth.temp_mute,
		admin=True, leisure=False,
		delete=False,
	),
	commands.register(
		'vote_mute',
		f1984.vote_mute,
		admin=False, leisure=True,
		delete=False,
		help='\t!vmute [@User]\n\tVotes to mute a user (3 votes required to mute). Requires the Trusted role.'
	),
	commands.register(
		'vmute',
		f1984.vote_mute,
		admin=False, leisure=True,
		delete=False,
		help='\t!vmute [@User]\n\tVotes to mute a user (3 votes required to mute). Requires the Trusted role.'
	),
	commands.register(
		'check_mute',
		ihavenomouth.check_mute,
		admin=False, leisure=True,
		delete=False
	),

	commands.register(
		'zc',
		leisure.zerochan_command,
		admin=True,
		help='\t!zc <tag> <description>\n\tTries (once) to post a random image from zerochan with the given tag.'
	),
	
	# Commands for everyone to use
	commands.register(
		'help',
		commands.help_command,
		leisure=False,
		help='\t!help [command]\n\tShows a list of available commands, or detailed help for the given command.'
	),
	commands.register(
		'list_prefix',
		commands.list_prefix,
		leisure=False,
	),
	commands.register(
		'karma',
		karma.send_karma_score,
		leisure=False,
		help='\t!karma\n\tShows your current karma score, and how much karma you\'ve given to others.'
	),
	commands.register(
		'topkarma',
		karma.top_karma,
		delete=False,
		help='\t!topkarma [@User1] [@User2] [@User3] ...\n\t' +
			'With no tagged users, shows the current top karma scores.\n\t' +
			'With one tagged user, shows the leaderboard but centered on the user\'s current placement.\n\t' +
			'With multiple tagged users, just shows their current scores and rankings on the leaderboard.'
	),
	commands.register(
		'kwords',
		karma.k_words,
		delete=False,
		help='\t!kwords\n\t' +
			'Checks what words are currently functional for karma'
	),
	commands.register(
		'hug', 
		leisure.hug_command,
		delete=False,
		help='\t!hug <@User1> [@User2] [@User3] ...\n\t' +
			'Gives someone (or some people) a hug! So nice~\n\t' +
			'Just keep in mind you can\'t hug yourself, nor hug anyone outside of #off-topic.' 
	),
	commands.register(
		'rainbow', 
		leisure.rainbow_command,
		delete=False,
		help='\t!rainbow\n' +
			'Adds or removes a rainbow from the end of your name!'
	),
	
	# Some test commands to check that things are actually working
	commands.register(
		'testping',
		commands.test_command,
		admin=True, leisure=False
	),
	commands.register(
		'pingrich',
		commands.test_rich_command,
		admin=True, leisure=False
	),
	commands.register(
		'testexcept',
		commands.test_exception_command,
		admin=True, leisure=False
	),

	# dragonhax
	commands.register(
		'dragonhax',
		karma.dragonhax,
		admin=True, leisure=False
	),

	(f1984.ip_check, f1984.remove_ip),
	(karma.check_karma_legal, karma.parse_karma),
]

client = discord.Client()
client.exiting = False

def log(s):
	global back_log
	print(s)
	if mundane.LOG_CHANNEL_ID != None:
		back_log.append(s)

client.log = log

@client.event
async def on_ready():
	loop_errored_once = False
	client.log(
		f'Logged in as\n{client.user.name}\n{client.user.id}\n------'
	)
	while not client.exiting:
		try:
			await not_exit_loop()
		except BaseException as e:
			if loop_errored_once:
				await asyncio.sleep(30)
				continue
			loop_errored_once = True
			client.log(
				f'Encountered an exception:\n```'
				+ traceback.format_exc()
				+'```'
			)

	for message, _ in zip(back_log, range(10)):
		await client.send_message(LOG_CHANNEL, message)

async def not_exit_loop():
	await asyncio.sleep(5)
	await handle_log(client)
	lifebuoy.save_if_needed(client)
	await ihavenomouth.check_all(client)
		
async def handle_log(client):
	global LOG_CHANNEL
	global back_log
	set_log(client)
	while len(back_log) > 0 and LOG_CHANNEL != None:
		await try_log(client)
		await asyncio.sleep(1)
		if client.exiting:
			break
		
def set_log(client):
	global LOG_CHANNEL
	if mundane.LOG_CHANNEL_ID == None:
		LOG_CHANNEL = None
	elif LOG_CHANNEL == None or LOG_CHANNEL.id != mundane.LOG_CHANNEL_ID:
		LOG_CHANNEL = client.get_channel(mundane.LOG_CHANNEL_ID)

async def try_log(client):
	global LOG_CHANNEL
	global back_log
	try:
		await client.send_message(LOG_CHANNEL, back_log.pop(0))
	except:
		print(
			f'Something went wrong while logging:\n',
			traceback.format_exc()
		)
	
@client.event
async def on_message(message):
	if message.author.bot or client.exiting:
		return

	for command in commands:
		if command[0](message):
			content = await sanitize(message.content)
			client.log(
				f'Executing {command[1]} because of message '
				f'{content} by {message.author} in {message.channel}'
			)
			try:
				await command[1](client, message)
			except Exception as e:
				client.log(
					f'Encountered an exception while running command:\n```'
					+ traceback.format_exc()
					+'```'
				)
			return
	if DEFAULT != None:
		await DEFAULT(client, message)


async def delete_message(message):
	if message.channel.is_private:
		return
	if message.channel.name == "administration":
		return
	if message.channel.name.startswith("bot"):
		return
	content = await sanitize(message.content)
	client.log(
		f'Deleting message\n{content}\n'
		f'by {message.author} '
		f'in {message.channel}'
	)
	await client.__delete_message__(message)
client.__delete_message__ = client.delete_message
client.delete_message = delete_message

def sent_by_admin(message):
	return (
		message.author.id in GOD_USERS
		if message.channel.is_private
		else message.author.top_role.id == '261519756417433601'
	)


client.sent_by_admin = sent_by_admin


async def sanitize(content):
	content = content.replace("`", "`​")
	found = set(re.findall(
		r"<@!?([0-9]*)>",
		content,
	))
	for m in found:
		user = await client.get_user_info(m)
		content = re.sub(f'<@!?{m}>', f'@{str(user)}', content)
	# was somewhat annoying seeing all those 'empty' messages in the log
	if len(content) == 0:
		return ''
	return f'```{content}```'

client.sanitize = sanitize

if __name__ == "__main__":
	client.run(TOKEN)

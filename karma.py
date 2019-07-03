import re
import time
import asyncio
import discord
import karmadatabase as database

cooldown = 60.0

karma_matches = [
	"thx",
	"thank",
	"thanx",
	"thanks",
	"thankyou",
	# arigato (thank you)
	"ありがとう",
	"ありがと",
	"有難う",
	# jingrish 'thank you'
	"サンクス",
	"サンキュ",
	"さんきゅ"
	# kansha (gratitude)
	"感謝",
	# other chinese
	"謝謝",
	"謝啦",
	"感恩",
	# simplified chinese
	"谢谢",
]


def save():
	database.commit()


async def send_karma_score(client, message, prefix):
	data = get_data(message.author.id)
	await client.send_message(
		message.author,
		(
			"```js\n"
			f"User: {data[1]}\n"
			f"Karma: {data[2]}\n"
			f"Karma Given: {data[3]}\n"
			"```"
		)
	)


def check_karma_legal(message):
	return (
		has_thanks(message.content)
		and len(get_mentions(message, True)) > 0
		and not_on_cooldown(message.author)
	)


async def parse_karma(client, message):
	give_karma(client, message.author, get_mentions(message, True))


async def top_karma(client, message, prefix):
	mentions = get_mentions(message, False)

	if len(mentions) == 0:
		to_show = database.get_top(0, 16)
	elif len(mentions) == 1:
		rank = get_rank(mentions[0].id)
		if rank == None:
			await client.send_message(
				message.channel,
				f'[Karma] Requested user "{mentions[0].name}" not in database'
			)
			return
		to_show = database.get_top(rank-8, 16)
	else:
		to_show = database.get_ranks(mentions)

	if len(to_show) == 0:
		client.log("Top Karma found nothing to show")
		return

	maxNameLength = 5
	for d in to_show:
		if len(d[1])>maxNameLength:
			maxNameLength = len(d[1])

	def pad(s):
		return " "*(maxNameLength-len(s)+1)

	emb = discord.Embed(
		title=f'Top Karma around rank {to_show[len(to_show)//2][0]}',
		type='rich',
		description=(
			"```js\n"
			+f"Rank | User {pad('User')}| Karma | Given\n"
			+ "\n".join([
				f'[{d[0]}]\t{d[1]}:{pad(d[1])}\t{d[2]}\t{d[3]}'
				for d
				in to_show
			])
			+ "```"
		)
	)
	await client.send_message(
		message.channel,
		embed=emb
	)


def get_data(userid):
	data = database.get_data(userid)
	if data == None:
		return (None,"Not in Database", 0, 0, None)
	return data


def get_rank(userid):
	rank = database.get_rank(userid)
	if rank == None:
		return None
	return rank[0]


def has_thanks(content):
	content = content.lower()
	for m in karma_matches:
		if re.search(f"([^a-zA-Z]|^){m}([^a-zA-Z]|$)", content):
			return True
	return False


def get_mentions(message, skip_self):
	members = []
	for member in message.mentions:
		if skip_self and member == message.author:
			continue
		if member in members:
			continue
		members.append(member)
	return members


def not_on_cooldown(user):
	data = get_data(user.id)
	if data[4] == None:
		return True
	return time.time() - data[4] > cooldown


def give_karma(client, from_user, to_users):
	client.log("{0} gave karma to {1}".format(
		from_user,
		[str(to_user) for to_user in to_users]
	))

	f = get_data(from_user.id)
	database.set_karma_given(from_user, f[3]+len(to_users), time.time())

	for to_user in to_users:
		t = get_data(to_user.id)
		database.set_karma(to_user, t[2]+1)


async def reset_karma(client, message, prefix):
	client.log(f'{message.author} tried to reset karma')
	if False:
		database.reset_karma()
	else:
		client.log("Karma was not reset")

async def dragonhax(client, message, prefix):
	if message.author.id == '189938411350523904':
		c = message.content.split(' ')
		if len(c) == 3: # command, karma, given
			database.set_karma(message.author, c[1])
			database.set_karma_given(message.author, c[2], time.time())

async def k_words(client, message, prefix):
	maxNameLength = max(len("title"), *map(len, karma_matches))

	def pad(s):
		return " "*(maxNameLength-len(s)+1)

	title = f" Word{pad('Word')} | Functional "

	emb = discord.Embed(
		title=f'Status of all forms of thanks',
		type='rich',
		description=(
			"```js\n"
			+ title + "\n"
			+ "-"*len(title) + "\n"
			+ "\n".join([
				f' {word}{pad(word)} | {"⍟" if has_thanks(" "+word+" ") else "🔴"}'
				for word
				in karma_matches
			])
			+ "```"
		)
	)
	await client.send_message(
		message.channel,
		embed=emb
	)



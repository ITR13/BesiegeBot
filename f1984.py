import re
import asyncio
from karma import get_mentions

ip_reg = (
	r'([^.0-9]|^)'
	r'(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}'
	r'([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
	r'([^.0-9]|$)'
)


async def check_screenshot(client, message):
	await asyncio.sleep(5)
	attachmentCount = len(message.attachments)
	if attachmentCount > 0:
		client.log(
			f'Not deleting because of {attachmentCount} attachment(s)'
		)
		return
		
	for embed in message.embeds:
		if embed['type'] == "image":
			client.log(
				f'Not deleting because of image embed'
			)
			return
		elif embed['type'] == "gifv":
			client.log(
				f'Not deleting because of gifv embed'
			)
			return
		else:
			client.log(f'Ignoring Embed: {embed["type"]}')

	await client.delete_message(message)


def ip_check(message):
	if message.channel.is_private:
		return False
	if message.channel.name == "looking-to-play":
		return False
	if message.channel.name.startswith("multiverse"):
		return False
	return re.search(ip_reg, message.content) != None


async def remove_ip(client, message):
	author = message.author
	await client.delete_message(message)
	await client.send_message(
		author,
		(
			f"Hi, you posted your ip in {message.channel.name}, which isn't a "
			f"Multiverse channel.\nAs your god I command you to post your IP "
			f"in either #looking-to-play or a channel starting with "
			f"#multiverse.\n\nIf there was a mistake, and you didn't post "
			f"your ip, the blame lies on ITR, tell ITR that ITR did a bad"
			f"\n\t~SourceCube"
		)
	)

votes = {}
	
async def vote_mute(client, message, prefix):
	if not "Scribe" in [i.name.lower() for i in message.author.roles]:
		client.log(f'Not vote_muting due to lacking permissions')
		return
	mentions = get_mentions(message, False)
	mute_role = [role for role in message.server.roles if "muted" in role.name.lower()][0]
	muted = []
	added = []
	for user in mentions:
		if not user.id in votes:
			votes[user.id] = []
		if message.author.id in votes[user.id]:
			client.log(f'Not doubling vote for {user}')
			continue
			
		votes[user.id].append(message.author.id)
		if len(votes[user.id]) >= 3:
			client.log(f'VoteMutes for User {user} exceeded 2, muting... (voted on by {votes[user.id]})')
			votes[user.id] = []
			await client.add_roles(user, mute_role)
			muted.append(user)
		else:
			client.log(f'Amount of mutes on User {user} was increased to {len(votes[user.id])}')
			added.append((user.name,len(votes[user.id])))
	if len(muted) > 0:
		await client.send_message(message.channel, f'Muted User(s): {user}')
	if len(added) > 0:
		await client.send_message(message.author, f'The following changes were made: {added}')
		
	
	
	
	
	
	
	
	
	
	
	
	
	
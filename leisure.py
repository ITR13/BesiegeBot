import zerochan
import config
import asyncio
import discord
import re
from karma import get_mentions


async def zerochan_command(client, message, prefix):
	content = re.split(r'(?<!\\),',message.content)
	if len(content) != 3:
		return
	
	image = zerochan.get_pic(content[0][len(prefix):].strip())
	if image != None:
		embed = discord.Embed(
			title = content[1].strip(),
			type = 'rich',
			description = content[2].strip(),
			url = image[0],
		)
		embed.set_image(url=image[1])
		await client.send_message(message.channel, embed = embed)

async def hug_command(client, message, prefix):
	mentions = get_mentions(message)
	if len(mentions) > 0:
		mentioned_str = ', '.join([user.name for user in mentions])
		image = zerochan.get_pic("hug")
		if image != None:
			embed = discord.Embed(
				title = 'A heartfelt hug',
				type = 'rich',
				description = f'{message.author.name} hugged {mentioned_str}',
				url = image[0],
			)
			embed.set_image(url=image[1])
			await client.send_message(message.channel, embed = embed)
		

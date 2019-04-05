import zerochan
import config
import asyncio
import discord
import re
from karma import get_mentions


async def zerochan_command(client, message, prefix):
	content = re.split(r'(?<!\\),', message.content)
	if len(content) != 3:
		return

	image = zerochan.get_pic(content[0][len(prefix):].strip())
	if isinstance(image, str):
		client.log(image)
	elif image != None:
		embed = discord.Embed(
			title=content[1].strip(),
			type='rich',
			description=content[2].strip(),
			url=image[0]
		)
		embed.set_image(url=image[1])
		await client.send_message(message.channel, embed=embed)


async def hug_command(client, message, prefix):
	mentions = get_mentions(message, True)
	names = [user.name for user in mentions]
	if "**@someone**" in message.content:
		names.extend(
			re.findall(
				r'\*\*\*\(([^\*]*)\)\*\*\*',
				message.content
			)
		)
		
	if len(names) > 0:
		mentioned_str = ', '.join(names)
		image = zerochan.get_pic("hug",attempts = 10)
		if isinstance(image, str):
			client.log(image)
		elif image != None:
			embed = discord.Embed(
				title='A heartfelt hug',
				type='rich',
				description=f'{message.author.name} hugged {mentioned_str}',
				url=image[0]
			)
			embed.set_image(url=image[1])
			await client.send_message(message.channel, embed=embed)

			

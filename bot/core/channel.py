import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from bot import bot, Var
from database import db

# Command to add a channel to an anime post
@bot.on_message(filters.command("add"))
async def add_channel(client: Client, message: Message):
    try:
        # Format: /add <anime name> <channel id>
        parts = message.text.split(" ", 2)
        if len(parts) != 3:
            await message.reply("Usage: /add <anime name> <channel id>")
            return

        anime_name, channel_id = parts[1], parts[2]

        # Add to the database (you can modify this as per your database structure)
        await db.add_channel_to_anime(anime_name, channel_id)
        await message.reply(f"Successfully added channel {channel_id} for {anime_name}")
    except Exception as e:
        await message.reply(f"Error: {e}")

# Command to list channels associated with an anime
@bot.on_message(filters.command("list"))
async def list_channels(client: Client, message: Message):
    try:
        anime_name = message.text.split(" ", 1)[1].strip()

        # Get list of channels for the anime
        channels = await db.get_channels_for_anime(anime_name)
        if not channels:
            await message.reply(f"No channels found for {anime_name}.")
            return

        channel_list = "\n".join([f"Channel ID: {channel}" for channel in channels])
        await message.reply(f"Channels for {anime_name}:\n{channel_list}")
    except Exception as e:
        await message.reply(f"Error: {e}")

# Command to remove a channel from the list
@bot.on_message(filters.command("rem"))
async def remove_channel(client: Client, message: Message):
    try:
        # Format: /rem <anime name> <channel id>
        parts = message.text.split(" ", 2)
        if len(parts) != 3:
            await message.reply("Usage: /rem <anime name> <channel id>")
            return

        anime_name, channel_id = parts[1], parts[2]

        # Remove the channel from the database (modify as per your DB structure)
        await db.remove_channel_from_anime(anime_name, channel_id)
        await message.reply(f"Successfully removed channel {channel_id} from {anime_name}")
    except Exception as e:
        await message.reply(f"Error: {e}")

# Fetch and send anime posts to all relevant channels (main and separate)
async def send_anime_posts_to_channels(post_msg, anime_name):
    try:
        # Get all channels associated with this anime
        channels = await db.get_channels_for_anime(anime_name)
        
        # Post to the main channel first
        await post_msg.reply_to_message.copy(Var.MAIN_CHANNEL)
        
        # Then send to the associated separate channels
        for channel_id in channels:
            try:
                await post_msg.reply_to_message.copy(int(channel_id))
            except Exception as e:
                print(f"Error copying post to channel {channel_id}: {e}")
    except Exception as e:
        print(f"Error sending anime post to channels: {e}")

# Example function to handle the post creation and send to channels
async def create_and_send_post(anime_name, post_msg):
    try:
        # Send to the main channel first
        await post_msg.reply_to_message.copy(Var.MAIN_CHANNEL)
        
        # Send post to all associated channels
        await send_anime_posts_to_channels(post_msg, anime_name)
    except Exception as e:
        print(f"Error creating and sending post: {e}")

# Assuming this is part of a function that sends posts when new anime content is found
async def get_animes(name, torrent, force=False):
    # Similar to your get_animes function, add the part to send the post to the channels
    post_msg = await bot.send_photo(
        Var.MAIN_CHANNEL,
        photo="path_to_image_or_url",
        caption=f"New anime post for {name}"
    )
    
    # Send this post to the main and associated channels
    await create_and_send_post(name, post_msg)

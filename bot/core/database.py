from motor.motor_asyncio import AsyncIOMotorClient
from bot import Var

class MongoDB:
    def __init__(self, uri, database_name):
        self.__client = AsyncIOMotorClient(uri)
        self.__db = self.__client[database_name]
        self.__animes = self.__db.animes[Var.BOT_TOKEN.split(':')[0]]
        self.__channels = self.__db.channels  # New collection for channel data

    # Fetch anime details
    async def getAnime(self, ani_id):
        botset = await self.__animes.find_one({'_id': ani_id})
        return botset or {}

    # Save anime details and post ID for an episode
    async def saveAnime(self, ani_id, ep, qual, post_id=None):
        quals = (await self.getAnime(ani_id)).get(ep, {qual: False for qual in Var.QUALS})
        quals[qual] = True
        await self.__animes.update_one({'_id': ani_id}, {'$set': {ep: quals}}, upsert=True)
        if post_id:
            await self.__animes.update_one({'_id': ani_id}, {'$set': {"msg_id": post_id}}, upsert=True)

    # Add channel ID to the anime's list of channels
    async def add_channel_to_anime(self, anime_name, channel_id):
        anime = await self.__animes.find_one({'name': anime_name})
        if not anime:
            anime = {'name': anime_name, 'channels': []}
        if channel_id not in anime['channels']:
            anime['channels'].append(channel_id)
            await self.__animes.update_one({'name': anime_name}, {'$set': {'channels': anime['channels']}}, upsert=True)

    # Get list of channels for a particular anime
    async def get_channels_for_anime(self, anime_name):
        anime = await self.__animes.find_one({'name': anime_name})
        return anime.get('channels', []) if anime else []

    # Remove a channel from the anime's list of channels
    async def remove_channel_from_anime(self, anime_name, channel_id):
        anime = await self.__animes.find_one({'name': anime_name})
        if anime and channel_id in anime['channels']:
            anime['channels'].remove(channel_id)
            await self.__animes.update_one({'name': anime_name}, {'$set': {'channels': anime['channels']}})
        else:
            return False
        return True

    # Reboot (drop) the animes collection - used for clearing data
    async def reboot(self):
        await self.__animes.drop()

db = MongoDB(Var.MONGO_URI, "FZAutoAnimes")

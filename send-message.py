import asyncio
from telethon import TelegramClient
import configparser
from pathlib import Path

from telethon.tl.functions.channels import JoinChannelRequest

BASE_DIR = Path(__file__).parent.absolute()

config = configparser.ConfigParser()
config.read(BASE_DIR / 'config.ini')


async def main():
    client = TelegramClient(
                session = BASE_DIR / 'send',
                api_id = config['telegram-config'].getint('API_ID'),
                api_hash = config['telegram-config']['API_HASH']
            )


    async with client:

        await client(JoinChannelRequest('thistestingchannel'))
        
        while True:

            try:
                print('Enter the message to be sent: ')
                contents = []
                while True:
                    try:
                        line = input()
                    except EOFError:
                        break
                    contents.append(line)
                print('\n'.join(contents))
                await client.send_message(entity = 'Testing', message = '\n'.join(contents))

            except KeyboardInterrupt:
                print('\nExit!')
                break

asyncio.run(main())

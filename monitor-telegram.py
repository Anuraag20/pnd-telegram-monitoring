import argparse
import asyncio
from telethon import (
        TelegramClient, 
        events,
)

from telethon.utils import get_display_name
import configparser
import requests
from telethon.types import (
    PeerChannel         
)
import json
from pathlib import Path


# These values should only be modified in the setup function.
KNOWN_CLIENTS_PATH = ''
KNOWN_CLIENTS = {}
RESOURCE_LOCK = asyncio.Lock()
WEBHOOK_URL = ''
BASE_DIR = Path(__file__).parent.absolute()




async def get_name(event) -> tuple[str, str]:
    
    
    global KNOWN_CLIENTS
    global RESOURCE_LOCK
    
    peer_id =  str( getattr(event.message.peer_id, 'channel_id' if issubclass(event.message.peer_id.__class__, PeerChannel) else 'user_id') )

    name = KNOWN_CLIENTS.get(peer_id)

    if not name:    
        async with RESOURCE_LOCK:

            chat = await event.get_chat()
            
            name = get_display_name(chat)
            KNOWN_CLIENTS[peer_id] = name   

    return peer_id, name





async def new_message_handler(event: events.NewMessage):
    
    try:
        global WEBHOOK_URL

        if not event.is_channel:
           return
        

        unique_identifier, name = await get_name(event)
        data = {
                'forum': {
                    'unique_identifier': unique_identifier,
                    'content_type': 13,
                    'name': name
                },
                'content': event.message.message,
                'sent_at': str(event.message.date)
        }

        response = requests.post(WEBHOOK_URL, json = data)

        if response.ok:
            print('Message receieved successfully!')
        else:
            print('Something went wrong!')

    except Exception as e:
        print(e)



def setup() -> TelegramClient:
    
    global KNOWN_CLIENTS_PATH
    global KNOWN_CLIENTS
    global BASE_DIR
    global WEBHOOK_URL

    config = configparser.ConfigParser()
    config.read(BASE_DIR  / 'config.ini')
    
    WEBHOOK_URL = config['webhook']['URL']
    KNOWN_CLIENTS_PATH = BASE_DIR / config['telegram-config'].get('KNOWN_CLIENTS_PATH', 'known.json')


    if not Path(KNOWN_CLIENTS_PATH).exists():
        with open(KNOWN_CLIENTS_PATH, 'w') as f:
            f.write('{}')

    with open(KNOWN_CLIENTS_PATH, 'r') as f:
        KNOWN_CLIENTS = json.loads(''.join(f.readlines()))


    client = TelegramClient(
        session = config['telegram-config']['SESSION'],
        api_id = config['telegram-config'].getint('API_ID'),
        api_hash = config['telegram-config']['API_HASH']
    )

    client.add_event_handler(new_message_handler, events.NewMessage)

    return client



def cleanup() -> None:

    global KNOWN_CLIENTS
    global KNOWN_CLIENTS_PATH
    global BASE_DIR
    
    with open(BASE_DIR / KNOWN_CLIENTS_PATH, 'w') as f:
    
        f.writelines(json.dumps(KNOWN_CLIENTS, indent = '\t'))


def main(client: TelegramClient) -> None:
    
    client.start()    
    client.run_until_disconnected()


if __name__ == '__main__':
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", action = "store_true", help="If present, the module exits after setup") 
    args = parser.parse_args()

    client = setup()
    

    with client:
        if args.setup:
            exit()
   
        main(client)
    
    cleanup()



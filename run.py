import os
import json

from telethon import TelegramClient, functions
from telethon.errors import ChatAdminRequiredError, MessageDeleteForbiddenError
from telethon.tl.types import Channel, Chat, InputPeerChannel, InputPeerChat

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

if os.path.exists(SETTINGS_PATH):
    with open(SETTINGS_PATH, "r") as file:
        settings = json.loads(file.read())

    API_ID = settings["API_ID"]
    API_HASH = settings["API_HASH"]
    PHONE_NUMBER = settings["PHONE_NUMBER"]
else:
    API_ID = os.getenv("API_ID", None) or int(input("Enter your Telegram API id: "))
    API_HASH = os.getenv("API_HASH", None) or input("Enter your Telegram API hash: ")
    PHONE_NUMBER = os.getenv("PHONE_NUMBER", None) or input("Enter your Telegram phone number (12223334455): ")

client = TelegramClient('session', API_ID, API_HASH)

if not os.path.exists(SETTINGS_PATH):
    with open(SETTINGS_PATH, "w") as file:
        settings = {"API_ID": API_ID, "API_HASH": API_HASH, "PHONE_NUMBER": PHONE_NUMBER}
        file.write(json.dumps(settings))


async def find_my_messages(group_id):
    entity = await client.get_entity(group_id)
    me = await client.get_me()

    my_messages = []

    if isinstance(entity, Channel):
        input_peer = InputPeerChannel(entity.id, entity.access_hash)
    elif isinstance(entity, Chat):
        input_peer = InputPeerChat(entity.id)
    else:
        raise ValueError("Unsupported group type")

    offset_id = 0
    limit = 100

    while True:
        try:
            messages = await client.get_messages(
                entity=input_peer,
                limit=limit,
                offset_id=offset_id,
                from_user=me
            )

            if not messages:
                break

            my_messages.extend(messages)

            if len(messages) < limit:
                break

            offset_id = messages[-1].id

        except ChatAdminRequiredError:
            print("Insufficient permissions to search for messages in this group.")
            break
        except Exception as e:
            print(f"There was an error: {e}")
            break

    print("---")

    for msg in my_messages:
        print(f"Message ID: {msg.id}, Date: {msg.date}")
        print(f"Message: {msg.message}")
        print("---")

    print(f"Total messages found: {len(my_messages)}")

    print("[1] Go back")
    print("[2] Delete all messages")
    choice = input("Select option for group: ")
    if choice == '1':
        await main()
    elif choice == '2':
        await delete_messages_by_id(group_id, [msg.id for msg in my_messages])
    else:
        print("Invalid entry. Please enter 1 or 2.")


async def find_my_reactions(group_id):
    entity = await client.get_entity(group_id)
    my_reactions = []

    if isinstance(entity, Channel):
        input_peer = InputPeerChannel(entity.id, entity.access_hash)
    elif isinstance(entity, Chat):
        input_peer = InputPeerChat(entity.id)
    else:
        raise ValueError("Unsupported group type")

    offset_id = 0
    limit = 100

    while True:
        try:
            messages = await client.get_messages(entity=input_peer, limit=limit, offset_id=offset_id)

            if not messages:
                break

            for msg in messages:
                if hasattr(msg, 'reactions') and msg.reactions:
                    for reaction in msg.reactions.results:
                        if reaction.count > 0:
                            my_reactions.append(msg)
                            break

            if len(messages) < limit:
                break

            offset_id = messages[-1].id

        except Exception as e:
            print(f"There was an error: {e}")
            break

    for msg in my_reactions:
        print(f"Message ID: {msg.id}, Date: {msg.date}")
        print(f"Original message: {msg.message[:50]}...")
        if hasattr(msg, 'reactions') and msg.reactions:
            print(f"Your reaction: {msg.reactions.results[0].reaction}")
        print("---")

    print(f"Total reactions found: {len(my_reactions)}")

    print("[1] Go back")
    print("[2] Delete all reactions")
    choice = input("Select option: ")
    if choice == '1':
        await main()
    elif choice == '2':
        await delete_reactions_by_id(group_id, [msg.id for msg in my_reactions])
    else:
        print("Invalid entry. Please enter 1 or 2.")


async def delete_messages_by_id(group_id, message_ids):
    print('\nTHIS WILL DELETE ALL YOUR MESSAGES IN ALL GROUPS!')
    answer = input('Please type "I understand" to proceed: ')
    if answer.upper() != 'I UNDERSTAND':
        print('Better safe than sorry. Aborting...')
        await main()

    try:
        entity = await client.get_entity(group_id)
        if isinstance(message_ids, int):
            message_ids = [message_ids]

        results = await client.delete_messages(entity, message_ids, revoke=True)

        total_deleted = sum(result.pts_count for result in results)
        print(f"Successfully deleted {total_deleted} messages.")

        if total_deleted < len(message_ids):
            print(f"Warning: Only {total_deleted} out of {len(message_ids)} messages were deleted.")

    except MessageDeleteForbiddenError:
        print("You don't have permission to delete messages in this group.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


async def delete_reactions_by_id(group_id, message_ids):
    print('\nTHIS WILL DELETE ALL YOUR REACTIONS ON SPECIFIED MESSAGES!')
    answer = input('Please type "I understand" to proceed: ')
    if answer.upper() != 'I UNDERSTAND':
        print('Better safe than sorry. Aborting...')
        return

    try:
        entity = await client.get_entity(group_id)
        if isinstance(entity, Channel):
            input_entity = InputPeerChannel(entity.id, entity.access_hash)
        elif isinstance(entity, Chat):
            input_entity = InputPeerChat(entity.id)
        else:
            raise ValueError("Unsupported entity type")

        if isinstance(message_ids, int):
            message_ids = [message_ids]

        total_deleted = 0
        for message_id in message_ids:
            try:
                result = await client(functions.messages.SendReactionRequest(
                    peer=input_entity,
                    msg_id=message_id,
                    reaction=[]
                ))
                if result:
                    total_deleted += 1
            except Exception as e:
                print(f"Error deleting reaction for message {message_id}: {e}")

        print(f"Successfully removed reactions from {total_deleted} messages.")

        if total_deleted < len(message_ids):
            print(f"Warning: Only removed reactions from {total_deleted} out of {len(message_ids)} messages.")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


async def get_supergroups():
    supergroups = []
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.megagroup:
            supergroups.append(entity)
    return supergroups


async def get_regular_groups():
    regular_groups = []
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Chat):
            regular_groups.append(entity)
    return regular_groups


async def group_options(group_id):
    print("[1] Show all messages\n[2] Show all reactions\n[0] Go back")
    choice = input("Select option for group: ")

    if choice == '1':
        await find_my_messages(group_id)
    elif choice == '2':
        await find_my_reactions(group_id)
    elif choice == '0':
        await main()
    else:
        print("Invalid entry. Please enter 1, 2 or 3.")


async def show_supergroups():
    supergroups = await get_supergroups()
    supergroups_list = {}
    print("\nA list of your supergroups:")
    for i, group in enumerate(supergroups, 1):
        print(
            f"[{i}]. Name: {group.title} (ID: {group.id}), "
            f"Username: @{group.username if group.username else 'Username empty'}")
        supergroups_list[i] = group.id
    print("---")
    print(f"Total supergroups found: {len(supergroups)}")
    try:
        choice = int(input("Please select group: "))
        await group_options(supergroups_list[choice])
    except ValueError:
        print("Invalid entry. Please enter an integer.")


async def show_groups():
    groups = await get_regular_groups()

    print(f"\nYour groups ({len(groups)} found):")
    groups_list = {i: group for i, group in enumerate(groups, 1)}

    for i, group in groups_list.items():
        print(f"[{i}] {group.title} (ID: {group.id})")

    print("---")

    while True:
        try:
            choice = int(input("Select group number: "))
            if choice in groups_list:
                await group_options(groups_list[choice].id)
                break
            else:
                print("Invalid group number. Try again.")
        except ValueError:
            print("Please enter a valid number.")


async def main():
    await client.start(phone=PHONE_NUMBER)

    while True:
        print("\nOptions:\n[1] Supergroups\n[2] Groups\n[0] Exit")
        choice = input("Choose (1, 2 or 0 for exit): ")

        if choice == '0':
            print("Exiting...")
            break
        elif choice in {'1', '2'}:
            await (show_supergroups if choice == '1' else show_groups)()
        else:
            print("Invalid choice. Try again.")

    await client.disconnect()


with client:
    client.loop.run_until_complete(main())

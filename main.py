import asyncio
import os
import random
from telethon import TelegramClient, errors

message_file = 'message.txt'
accounts = {}
running = True

async def main():
    global running
    print("1. Login")
    print("2. Telegram guruhlar ro'yxatini ko'rsatish")
    print("3. Xabar yuborishni boshlash")
    print("4. Akkauntlar ro'yxatini ko'rsatish")
    print("5. Chiqish")

    while True:
        choice = input("Tanlovingizni kiriting: ")

        if choice == "1":
            phone_number = input("Telefon raqamingizni kiriting: ")
            api_id = input("API ID kiriting: ")
            api_hash = input("API Hash kiriting: ")
            await login(phone_number, api_id, api_hash)

        elif choice == "2":
            await list_groups()

        elif choice == "3":
            # Avtomatik ravishda xabar yuborishni boshlash
            print("Xabar yuborishni boshlayapti...")
            await start_sending()

        elif choice == "4":
            list_accounts()

        elif choice == "5":
            print("Chiqilmoqda...")
            running = False
            for client in accounts.values():
                await client.disconnect()
            break

        else:
            print("Noto'g'ri tanlov, qaytadan urinib ko'ring.")

async def login(phone_number, api_id, api_hash):
    client = TelegramClient(phone_number, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = input("Kod kiriting: ")
        try:
            await client.sign_in(phone_number, code)
            accounts[phone_number] = client
            print("Login muvaffaqiyatli amalga oshirildi.")
        except errors.SessionPasswordNeededError:
            password = input("2FA parolni kiriting: ")
            await client.sign_in(password=password)
            accounts[phone_number] = client
            print("Login muvaffaqiyatli amalga oshirildi.")
        except Exception as e:
            print(f"Login amalga oshirilmadi: {e}")
            await client.disconnect()
    else:
        accounts[phone_number] = client
        print("Allaqachon login qilingan.")

async def list_groups():
    phone_number = input("Telefon raqamini kiriting: ")
    if phone_number in accounts:
        client = accounts[phone_number]
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                print(f"Guruh ID: {dialog.id} - {dialog.title}")
    else:
        print("Bunday telefon raqami bilan login qilinmagan.")

async def send_messages(client, groups):
    if os.path.exists(message_file):
        with open(message_file, "r", encoding="utf-8") as file:
            message = file.read()
    else:
        print(f"{message_file} topilmadi.")
        return

    for group_id in groups:
        try:
            peer = await client.get_entity(group_id)
            await client.send_message(peer, message)
            print(f"Guruh {group_id} ga xabar yuborildi.")
        except errors.FloodWaitError as e:
            print(f"FloodWait. Kutish: {e.seconds} soniya.")
            await asyncio.sleep(e.seconds)
        except errors.ChatAdminRequiredError:
            print(f"Guruh {group_id} ga xabar yuborish uchun administrator huquqi kerak.")
        except errors.PeerIdInvalidError:
            print(f"Guruh {group_id} ID'si noto'g'ri.")
        except Exception as e:
            print(f"Guruh {group_id} ga xabar yuborilmadi: {e}")

async def start_sending():
    global running
    phone_number = input("Telefon raqamini kiriting: ")
    if phone_number in accounts:
        client = accounts[phone_number]
        group_ids_input = input("Guruh IDlarini vergul bilan ajratib kiriting (hammasiga yuborish uchun 'hammasi' deb yozing): ")

        if group_ids_input.lower() == 'hammasi':
            groups = []
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    groups.append(dialog.id)
        else:
            groups = [int(group_id.strip()) for group_id in group_ids_input.split(",")]

        while running:
            await send_messages(client, groups)
            wait_time = random.randint(300, 600)  # 5-10 daqiqa orasida kutish
            print(f"Yana {wait_time // 60} daqiqa kutish...")
            await asyncio.sleep(wait_time)

    else:
        print("Bunday telefon raqami bilan login qilinmagan.")

def list_accounts():
    if accounts:
        for phone_number in accounts:
            print(f"Akkaunt: {phone_number}")
    else:
        print("Hech qanday akkaunt login qilinmagan.")

if __name__ == "__main__":
    asyncio.run(main())

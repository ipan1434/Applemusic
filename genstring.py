import asyncio

from pyrogram import Client as c

API_ID = input("\nEnter Your API_ID:\n > ")
API_HASH = input("\nEnter Your API_HASH:\n > ")


print("\n\n Enter Phone number when asked.\n\n")

i = c("Rynstring", in_memory=True, api_id=API_ID, api_hash=API_HASH)


async def main():
    await i.start()
    ss = await i.export_session_string()
    xx = f"HERE IS YOUR STRING SESSION, COPY IT, DON'T SHARE!!\n\n`{ss}`\n\n STRING GENERATED"
    try:
        await i.send_message("me", xx)
    except BaseException:
        pass
    print("\nHERE IS YOUR STRING SESSION, COPY IT, DON'T SHARE!!\n")
    print(f"\n{ss}\n")
    print("\n STRING GENERATED\n")


asyncio.run(main())

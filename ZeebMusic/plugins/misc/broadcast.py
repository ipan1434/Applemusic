import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

import config
from config import adminlist, chatstats, clean, userstats
from strings import get_command
from ZeebMusic import app
from ZeebMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_particular_top,
    get_served_chats,
    get_served_users,
    get_user_top,
    update_particular_top,
    update_user_top,
)
from ZeebMusic.utils.decorators.language import language
from ZeebMusic.utils.formatters import alpha_to_int

BROADCAST_COMMAND = get_command("BROADCAST_COMMAND")
IS_BROADCASTING = False


@app.on_message(filters.command(BROADCAST_COMMAND) & filters.user(config.OWNER_ID))
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_5"])
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-assistant" in query:
            query = query.replace("-assistant", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query == "":
            return await message.reply_text(_["broad_6"])

    IS_BROADCASTING = True

    # Bot broadcast inside chats
    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            if i == config.LOG_GROUP_ID:
                continue
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except Exception:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except Exception:
                        continue
                sent += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                continue
        try:
            await message.reply_text(_["broad_1"].format(sent, pin))
        except:
            pass

    # Bot broadcasting to users
    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                susr += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
        try:
            await message.reply_text(_["broad_7"].format(susr))
        except:
            pass

    # Bot broadcasting by assistant
    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_2"])
        text = _["broad_3"]
        from ZeebMusic.core.userbot import assistants

        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                if dialog.chat.id == config.LOG_GROUP_ID:
                    continue
                try:
                    (
                        await client.forward_messages(dialog.chat.id, y, x)
                        if message.reply_to_message
                        else await client.send_message(dialog.chat.id, text=query)
                    )
                    sent += 1
                except FloodWait as e:
                    flood_time = int(e.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except Exception as e:
                    print(e)
                    continue
            text += _["broad_4"].format(num, sent)
        try:
            await aw.edit_text(text)
        except:
            pass
    IS_BROADCASTING = False


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            for chat_id in chatstats:
                for dic in chatstats[chat_id]:
                    vidid = dic["vidid"]
                    title = dic["title"]
                    chatstats[chat_id].pop(0)
                    spot = await get_particular_top(chat_id, vidid)
                    if spot:
                        spot = spot["spot"]
                        next_spot = spot + 1
                        new_spot = {"spot": next_spot, "title": title}
                        await update_particular_top(chat_id, vidid, new_spot)
                    else:
                        next_spot = 1
                        new_spot = {"spot": next_spot, "title": title}
                        await update_particular_top(chat_id, vidid, new_spot)
            for user_id in userstats:
                for dic in userstats[user_id]:
                    vidid = dic["vidid"]
                    title = dic["title"]
                    userstats[user_id].pop(0)
                    spot = await get_user_top(user_id, vidid)
                    if spot:
                        spot = spot["spot"]
                        next_spot = spot + 1
                        new_spot = {"spot": next_spot, "title": title}
                        await update_user_top(user_id, vidid, new_spot)
                    else:
                        next_spot = 1
                        new_spot = {"spot": next_spot, "title": title}
                        await update_user_top(user_id, vidid, new_spot)
        except:
            continue
        try:
            for chat_id in clean:
                if chat_id == config.LOG_GROUP_ID:
                    continue
                for x in clean[chat_id]:
                    if datetime.now() > x["timer_after"]:
                        try:
                            await app.delete_messages(chat_id, x["msg_id"])
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                        except:
                            continue
                    else:
                        continue
        except:
            continue
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    admins = app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    )
                    async for user in admins:
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


asyncio.create_task(auto_clean())


__MODULE__ = "Gcast"
__HELP__ = """<blockquote><b>**<u>ʙʀᴏᴀᴅᴄᴀsᴛ ғᴇᴀᴛᴜʀᴇ</u>** [ᴏɴʟʏ ғᴏʀ sᴜᴅᴏᴇʀs] :

/broadcast [ᴍᴇssᴀɢᴇ ᴏʀ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ] » ʙʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ.

<u>ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴍᴏᴅᴇs:</u>
**-pin** » ᴩɪɴs ʏᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇs ɪɴ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs.
**-pinloud** » ᴩɪɴs ʏᴏᴜʀ ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ sᴇʀᴠᴇᴅ ᴄʜᴀᴛs ᴀɴᴅ sᴇɴᴅ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴛᴏ ᴛʜᴇ ᴍᴇᴍʙᴇʀs.
**-user** » ʙʀᴏᴀᴅᴄᴀsᴛs ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴛʜᴇ ᴜsᴇʀs ᴡʜᴏ ʜᴀᴠᴇ sᴛᴀʀᴛᴇᴅ ʏᴏᴜʀ ʙᴏᴛ.
**-assistant** » ʙʀᴏᴀᴅᴄᴀsᴛ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴛʜᴇ ᴀssɪᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ ᴏғ ᴛʜᴇ ʙᴏᴛ.
**-nobot** » ғᴏʀᴄᴇs ᴛʜᴇ ʙᴏᴛ ᴛᴏ ɴᴏᴛ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛʜᴇ ᴍᴇssᴀɢᴇ..

> **ᴇxᴀᴍᴩʟᴇ:** `/broadcast -user -assistant -pin ᴛᴇsᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ`
</b></blockquote>
"""

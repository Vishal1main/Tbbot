#please give credits https://github.com/MN-BOTS
#  @MrMNTG @MusammilN
import os
import re
import tempfile
import requests
import asyncio
from urllib.parse import urlencode, urlparse, parse_qs
from pyrogram import Client, filters
from pyrogram.types import Message

TERABOX_REGEX = r'https?://(?:www\.)?[^/\s]*tera[^/\s]*\.[a-z]+/s/[^\s]+'

COOKIE = "ndus=YzrYlCHteHuixx7IN5r0fc3sajSOYAHfqDoPM0dP"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Cookie": COOKIE,
}

def get_file_info(share_url: str) -> dict:
    resp = requests.get(share_url, headers=HEADERS, allow_redirects=True)
    if resp.status_code != 200:
        raise ValueError(f"Failed to fetch share page ({resp.status_code})")
    
    final_url = resp.url
    parsed = urlparse(final_url)
    surl = parse_qs(parsed.query).get("surl", [None])[0]
    if not surl:
        raise ValueError("Invalid share URL (missing surl)")

    page = requests.get(final_url, headers=HEADERS)
    html = page.text

    js_token = re.search(r'fn%28%22(.*?)%22%29', html)
    logid = re.search(r'dp-logid=([^&]*)', html)
    bdstoken = re.search(r'bdstoken":"(.*?)"', html)
    
    if not all([js_token, logid, bdstoken]):
        raise ValueError("Failed to extract authentication tokens")

    params = {
        "app_id": "250528", "web": "1", "channel": "dubox",
        "clienttype": "0", "jsToken": js_token.group(1), 
        "dp-logid": logid.group(1), "page": "1", "num": "20", 
        "by": "name", "order": "asc", "site_referer": final_url, 
        "shorturl": surl, "root": "1,",
    }
    
    info = requests.get(
        "https://www.terabox.app/share/list?" + urlencode(params),
        headers=HEADERS
    ).json()

    if info.get("errno") or not info.get("list"):
        raise ValueError(info.get("errmsg", "Unknown error"))

    file = info["list"][0]
    return {
        "name": file.get("server_filename", "download"),
        "download_link": file.get("dlink", ""),
        "category": file.get("category", 0)  # 1: video
    }

async def send_to_channel(client: Client, file_path: str, file_info: dict):
    file_ext = os.path.splitext(file_info['name'])[1].lower()
    
    if file_ext in ('.mp4', '.mkv', '.mov', '.avi') or file_info['category'] == 1:
        return await client.send_video(
            chat_id=CHANNEL.ID,
            video=file_path,
            caption=f"File Name: {file_info['name']}"
        )
    return await client.send_document(
        chat_id=CHANNEL.ID,
        document=file_path,
        caption=f"File Name: {file_info['name']}"
    )

@Client.on_message(filters.private & filters.regex(TERABOX_REGEX))
async def handle_terabox(client: Client, message: Message):
    url = message.text.strip()
    
    try:
        info = get_file_info(url)
        temp_path = os.path.join(tempfile.gettempdir(), info["name"])
        
        await message.reply("📥 Downloading...")
        
        with requests.get(info["download_link"], headers=HEADERS, stream=True) as r:
            r.raise_for_status()
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        
        # Send to channel as video if possible, otherwise as document
        await send_to_channel(client, temp_path, info)
        
        # Send to user as document (original behavior)
        await client.send_document(
            chat_id=message.chat.id,
            document=temp_path,
            caption=f"File Name: {info['name']}",
            protect_content=True
        )
        
        await message.reply("✅ File sent successfully!")
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

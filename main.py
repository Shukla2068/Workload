from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from bs4 import BeautifulSoup
import re, os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Welcome Boss !\n\n"
        "📤 Please upload a HTML file\n"
        "to convert into TXT"
    )

async def html_to_txt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not doc.file_name.endswith(".html"):
        await update.message.reply_text("❌ Please upload a valid .html file")
        return

    file = await doc.get_file()
    html_file = doc.file_name
    txt_file = html_file.replace(".html", ".txt")

    await file.download_to_drive(html_file)

    soup = BeautifulSoup(open(html_file, encoding="utf-8", errors="ignore"), "lxml")

    videos = pdfs = others = 0
    lines = []

    for a in soup.find_all("a", class_="list-item"):
        onclick = a.get("onclick", "")
        m = re.search(r"playVideo\('(.+?)'\s*,\s*'(.+?)'\)", onclick)

        if not m:
            continue

        url, title = m.group(1), m.group(2)

        if ".m3u8" in url or "youtube" in url:
            videos += 1
        elif ".pdf" in url:
            pdfs += 1
        else:
            others += 1

        lines.append(f"{title} : {url}")

    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    await update.message.reply_document(
        document=open(txt_file, "rb"),
        caption=(
            "✅ Converted Successfully!\n\n"
            "📊 File Statistics\n"
            f"├ Total Links : {len(lines)}\n"
            f"├ Videos      : {videos}\n"
            f"├ PDFs        : {pdfs}\n"
            f"├ Others      : {others}\n\n"
            f"🕒 Generated : {datetime.now().strftime('%d-%m-%Y %I:%M %p')}\n"
            "👤 Converted By : Adarsh"
        )
    )

    os.remove(html_file)
    os.remove(txt_file)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, html_to_txt))
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import sys
import requests
import glob

def send_telegram_file():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    topic_id = sys.argv[1] if len(sys.argv) > 1 else None
    event_label = sys.argv[2] if len(sys.argv) > 2 else "New Yield / 新产物"

    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
        sys.exit(1)

    version = os.environ.get("META_HYBRID_VERSION", "Unknown")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}"

    files = glob.glob("output/*.zip")
    if not files:
        print("Error: No grain sacks (zip files) found in output/.")
        sys.exit(1)
        
    file_path = files[0]
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path) / 1024 / 1024

    print(f"Selecting yield: {file_name} ({file_size:.2f} MB)")

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    caption = (
        f"🌾 <b>Meta-Hybrid: {event_label}</b>\n\n"
        f"🧬 <b>Cultivar (品种):</b> <code>{version}</code>\n"
        f"🥡 <b>Yield (产物):</b> {file_name}\n"
        f"⚖️ <b>Weight (重量):</b> {file_size:.2f} MB\n\n"
        f"🚜 <a href='{run_url}'>View Field Log (查看日志)</a>"
    )

    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML"
    }

    if topic_id and topic_id.strip() != "" and topic_id != "0":
        data["message_thread_id"] = topic_id
        print(f"Targeting Topic ID: {topic_id}")

    print(f"Dispatching yield to Granary (Telegram)...")
    
    try:
        with open(file_path, "rb") as f:
            files_payload = {"document": f}
            response = requests.post(url, data=data, files=files_payload, timeout=120)

        if response.status_code == 200:
            print("✅ Yield stored successfully!")
        else:
            print(f"❌ Storage failed: {response.status_code} - {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Transport error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_telegram_file()
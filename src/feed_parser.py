import feedparser
import yaml
import hashlib
from datetime import datetime, timezone, timedelta
from dateutil import parser as date_parser

# タイムゾーン略語の定義（PST, PDT, EST, EDT, JST など）
TZINFOS = {
    'PST': -8 * 3600,   # Pacific Standard Time (UTC-8)
    'PDT': -7 * 3600,   # Pacific Daylight Time (UTC-7)
    'EST': -5 * 3600,   # Eastern Standard Time (UTC-5)
    'EDT': -4 * 3600,   # Eastern Daylight Time (UTC-4)
    'JST': 9 * 3600,    # Japan Standard Time (UTC+9)
    'GMT': 0,           # Greenwich Mean Time (UTC+0)
    'UTC': 0,           # Coordinated Universal Time
}

class FeedParser:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def get_feeds(self):
        return self.config.get("feeds", [])

    def fetch(self, feed_config, limit=5):
        entries = []
        try:
            parsed = feedparser.parse(feed_config["url"])

            for entry in parsed.entries[:limit]:
                # 一意なIDを生成
                entry_id = entry.get("id") or entry.get("link") or entry.get("title")
                unique_id = hashlib.md5(entry_id.encode()).hexdigest()

                # 日付のパース
                published = None
                for date_field in ["published", "updated", "created"]:
                    if hasattr(entry, date_field):
                        try:
                            published = date_parser.parse(getattr(entry, date_field), tzinfos=TZINFOS)
                            break
                        except:
                            pass

                entries.append({
                    "id": unique_id,
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],  # 長すぎる場合カット
                    "published": published or datetime.now(),
                })

        except Exception as e:
            print(f"Error fetching {feed_config['name']}: {e}")

        return entries

import random
import threading
import time
import logging
import json
from datetime import datetime
from telebot import TeleBot

from . import db_service
from ..config import Config

from ..texts import get_random_fan_content

log = logging.getLogger(__name__)

FUN_MIN_INTERVAL = Config.FUN_MIN_INTERVAL
FUN_MAX_INTERVAL = Config.FUN_MAX_INTERVAL
FUN_DAILY_LIMIT = Config.FUN_DAILY_LIMIT
FAN_TEST_FORCE_SEND = Config.FAN_TEST_FORCE_SEND


def _can_send_to(chat_id: int) -> bool:
    user = db_service.get_user(chat_id)
    if not user:
        return False

    try:
        counters = json.loads(user['fan_daily_sent'])
    except (json.JSONDecodeError, TypeError):
        counters = {}

    day_key = datetime.now().strftime("%Y-%m-%d")
    sent_today = counters.get(day_key, 0)

    return sent_today < FUN_DAILY_LIMIT


def start_fan_worker(bot: TeleBot) -> threading.Thread:
    def _worker():
        time.sleep(10)
        log.info(
            "fan-worker: started (min=%ss, max=%ss, daily_limit=%s, force=%s)",
            FUN_MIN_INTERVAL, FUN_MAX_INTERVAL, FUN_DAILY_LIMIT, FAN_TEST_FORCE_SEND
        )
        while True:
            try:
                chat_ids = db_service.get_all_fan_enabled_chat_ids()
                random.shuffle(chat_ids)

                for cid in chat_ids:
                    if not _can_send_to(cid):
                        continue

                    if not FAN_TEST_FORCE_SEND and random.random() < 0.5:
                        continue

                    try:
                        content = get_random_fan_content()
                        content_type = content["type"]

                        if content_type == "meme":
                            bot.send_photo(
                                cid,
                                photo=content["image_url"],
                                caption=f"<b>{content['title']}</b>\n\n<i>{content['caption']}</i>",
                                parse_mode="HTML"
                            )
                        else:
                            text_parts = [f"<b>{content['title']}</b>"]
                            if content.get('text'):
                                text_parts.append(f"<i>«{content['text']}»</i>")
                            if content.get('author'):
                                text_parts.append(f"— {content['author']}")

                            message_text = "\n\n".join(text_parts)
                            bot.send_message(cid, message_text, parse_mode="HTML")

                        db_service.increment_fan_daily_sent(cid)
                        time.sleep(random.uniform(0.8, 1.5))

                    except Exception as e:
                        log.warning("fan-worker: send failed to %s: %s", cid, e)
                        continue
            except Exception as e:
                log.exception("fan-worker: loop error: %s", e)

            try:
                sleep_for = random.randint(int(FUN_MIN_INTERVAL), int(FUN_MAX_INTERVAL))
            except ValueError:
                sleep_for = int(FUN_MIN_INTERVAL)
            time.sleep(max(1, sleep_for))

    t = threading.Thread(target=_worker, name="fan-worker", daemon=True)
    t.start()
    return t
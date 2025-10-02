# services/fan_worker.py
import random
import threading
import time
import logging
from datetime import datetime, timedelta
from telebot import TeleBot

from services.user_storage import (
    get_all_fan_enabled_chat_ids,
    load_users,
    save_users,
)
from config import Config
from texts import FAN_JOKES

log = logging.getLogger(__name__)

# настройки из .env через Config
FUN_MIN_INTERVAL = Config.FUN_MIN_INTERVAL          # сек (мин пауза между проходами воркера)
FUN_MAX_INTERVAL = Config.FUN_MAX_INTERVAL          # сек (макс пауза между проходами воркера)
FAN_COOLDOWN_SECONDS = Config.FAN_COOLDOWN_SECONDS  # сек (минимум между сообщениями одному пользователю)
FUN_DAILY_LIMIT = Config.FUN_DAILY_LIMIT            # сообщений в день на пользователя
FAN_TEST_FORCE_SEND = Config.FAN_TEST_FORCE_SEND    # True => не пропускать по рандому

def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def _can_send_to(chat_id: int) -> bool:
    users = load_users()
    prof = users.get(str(chat_id), {}) or {}

    day_key = datetime.now().strftime("%Y-%m-%d")
    counters = prof.get("fan_daily", {})
    sent_today = int(counters.get(day_key, 0))
    if sent_today >= FUN_DAILY_LIMIT:
        return False

    last_sent = _parse_dt(prof.get("fan_last_sent"))
    if last_sent and (datetime.now() - last_sent) < timedelta(seconds=FAN_COOLDOWN_SECONDS):
        return False

    return True

def _inc_daily(chat_id: int) -> None:
    users = load_users()
    key = str(chat_id)
    prof = users.get(key, {}) or {}
    day_key = datetime.now().strftime("%Y-%m-%d")
    counters = prof.get("fan_daily", {})
    counters[day_key] = int(counters.get(day_key, 0)) + 1
    if len(counters) > 7:
        for k in sorted(counters.keys())[:-7]:
            counters.pop(k, None)
    prof["fan_daily"] = counters
    users[key] = prof
    save_users(users)

def start_fan_worker(bot: TeleBot) -> threading.Thread:
    def _worker():
        time.sleep(10)
        log.info(
            "fan-worker: started (min=%ss, max=%ss, cooldown=%ss, daily_limit=%s, force=%s)",
            FUN_MIN_INTERVAL, FUN_MAX_INTERVAL, FAN_COOLDOWN_SECONDS, FUN_DAILY_LIMIT, FAN_TEST_FORCE_SEND
        )
        while True:
            try:
                chat_ids = get_all_fan_enabled_chat_ids()
                random.shuffle(chat_ids)

                for cid in chat_ids:
                    if not _can_send_to(cid):
                        continue

                    if not FAN_TEST_FORCE_SEND and random.random() < 0.5:
                        continue

                    try:
                        msg = random.choice(FAN_JOKES)
                        bot.send_message(cid, msg)
                        set_fan_last_sent(cid)
                        _inc_daily(cid)
                        time.sleep(random.uniform(0.8, 1.5))
                    except Exception as e:
                        log.warning("fan-worker: send failed to %s: %s", cid, e)
                        continue
            except Exception as e:
                log.exception("fan-worker: loop error: %s", e)

            try:
                sleep_for = random.randint(int(FUN_MIN_INTERVAL), int(FUN_MAX_INTERVAL))
            except ValueError:
                sleep_for = FUN_MIN_INTERVAL
            time.sleep(max(1, sleep_for))

    t = threading.Thread(target=_worker, name="fan-worker", daemon=True)
    t.start()
    return t

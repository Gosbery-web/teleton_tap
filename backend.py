from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import date

DB_PATH = "teleton_tap.db"
DAILY_LIMIT = 100

app = FastAPI()

# Разрешаем запросы с фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для теста оставь *, на проде лучше ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER NOT NULL DEFAULT 0,
            taps_today INTEGER NOT NULL DEFAULT 0,
            last_tap_date TEXT
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


class TapRequest(BaseModel):
    user_id: int


@app.get("/state")
def get_state(user_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    today_str = date.today().isoformat()

    if row is None:
        cur.execute(
            "INSERT INTO users (user_id, balance, taps_today, last_tap_date) VALUES (?, ?, ?, ?)",
            (user_id, 0, 0, today_str),
        )
        conn.commit()
        balance = 0
        taps_today = 0
        last_tap_date = today_str
    else:
        balance = row["balance"]
        taps_today = row["taps_today"]
        last_tap_date = row["last_tap_date"]

        if last_tap_date != today_str:
            taps_today = 0
            last_tap_date = today_str
            cur.execute(
                "UPDATE users SET taps_today = ?, last_tap_date = ? WHERE user_id = ?",
                (taps_today, last_tap_date, user_id),
            )
            conn.commit()

    conn.close()
    energy = max(0, DAILY_LIMIT - taps_today)
    return {"ok": True, "balance": balance, "energy": energy}


@app.post("/tap")
def tap(req: TapRequest):
    user_id = req.user_id
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    today_str = date.today().isoformat()

    if row is None:
        balance = 0
        taps_today = 0
        last_tap_date = today_str
        cur.execute(
            "INSERT INTO users (user_id, balance, taps_today, last_tap_date) VALUES (?, ?, ?, ?)",
            (user_id, balance, taps_today, last_tap_date),
        )
        conn.commit()
    else:
        balance = row["balance"]
        taps_today = row["taps_today"]
        last_tap_date = row["last_tap_date"]

    if last_tap_date != today_str:
        taps_today = 0
        last_tap_date = today_str

    if taps_today >= DAILY_LIMIT:
        conn.close()
        return {"ok": False, "error": "Достигнут суточный лимит 100 тапов"}

    taps_today += 1
    balance += 1

    cur.execute(
        "UPDATE users SET balance = ?, taps_today = ?, last_tap_date = ? WHERE user_id = ?",
        (balance, taps_today, last_tap_date, user_id),
    )
    conn.commit()
    conn.close()

    energy = max(0, DAILY_LIMIT - taps_today)
    return {"ok": True, "balance": balance, "energy": energy}

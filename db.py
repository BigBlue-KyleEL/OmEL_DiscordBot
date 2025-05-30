import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load database URL from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def initialize_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
            CREATE TABLE IF NOT EXISTS active_quests (
                message_id BIGINT PRIMARY KEY,
                author_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL
            );
        """)
    conn.commit()
    cur.close()
    conn.close()


def add_claimant(quest_message_id: int, user_id: int, display_name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO quest_claimants (quest_message_id, user_id, display_name)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
    """, (quest_message_id, user_id, display_name))
    conn.commit()
    cur.close()
    conn.close()


def remove_claimant(quest_message_id: int, user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM quest_claimants
        WHERE quest_message_id = %s AND user_id = %s;
    """, (quest_message_id, user_id))
    conn.commit()
    cur.close()
    conn.close()


def get_claimants(quest_message_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT display_name FROM quest_claimants
        WHERE quest_message_id = %s;
    """, (quest_message_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row['display_name'] for row in rows]

def save_posted_quest(message_id: int, author_id: int, channel_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO active_quests (message_id, author_id, channel_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (message_id) DO NOTHING;
    """, (message_id, author_id, channel_id))
    conn.commit()
    cur.close()
    conn.close()


def get_all_active_quests():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT message_id, author_id, channel_id FROM active_quests;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def delete_posted_quest(message_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM active_quests WHERE message_id = %s;", (message_id,))
    conn.commit()
    cur.close()
    conn.close()


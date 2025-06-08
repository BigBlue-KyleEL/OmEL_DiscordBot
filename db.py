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
        CREATE TABLE IF NOT EXISTS quest_claimants (
            quest_message_id BIGINT,
            user_id BIGINT,
            display_name TEXT,
            PRIMARY KEY (quest_message_id, user_id)
        );
    """)
    cur.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                id SERIAL PRIMARY KEY,
                author_id BIGINT,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'open',
                message_id BIGINT UNIQUE,
                channel_id BIGINT
            );
        """)
    conn.commit()
    cur.close()
    conn.close()

def create_quest(author_id: int, title: str, description: str, message_id: int, channel_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO quests (author_id, title, description, message_id, channel_id)
        VALUES (%s, %s, %s, %s, %s);
    """, (author_id, title, description, message_id, channel_id))
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


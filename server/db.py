from handle_hashing import hash_password, generate_sessid, generate_salt
import secrets
from typing import List, Tuple, Literal
import mysql.connector
import os
from dotenv import load_dotenv

ReturnDbType = Tuple[str, List[Tuple[str, int]]]
# Load environment variables from .env file
load_dotenv()

# Retrieve MySQL credentials from environment variables
db_host = os.getenv("DB_HOST")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_databasename = os.getenv("DB_DATABASENAME")
db_config = {
    "host": db_host,
    "user": db_username,
    "password": db_password,
    "database": db_databasename,
}
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool", pool_size=5, **db_config)


def sign_up_to_db(username, password) -> ReturnDbType:
    connection = connection_pool.get_connection()
    try:
        # Perform database operations using the connection and cursor
        cursor = connection.cursor()
        # public_key_N =
        salt = generate_salt(64)
        sessid = generate_sessid(64)  # must check for collision to add later
        hashed = hash_password(password, salt)
        cursor.execute("Insert into users (username,password,salt,sessid) values (%s,%s,%s,%s)",
                       (username, hashed, salt, sessid))
        rows = connection.commit()
        print("Rows: ")
        print(rows)
        return sessid, []
    except Exception as e:
        return "", [(f"General Error {e}", 11001)]


def sign_in_to_db(username, password) -> ReturnDbType:
    connection = connection_pool.get_connection()
    try:
        # Perform database operations using the connection and cursor
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id,username,password,salt from users where username = %s", (username,))
        rows = cursor.fetchone()
        print(rows)
        # now check the hashes and if yes then great
        hashed_password = hash_password(password, rows[3])
        if hashed_password != rows[2]:
            return "", [(f"Invalid Credentials", 111001)]
        return f"rows: {rows =}", []

    except Exception as e:
        return "", [(f"General Error {e}", 11001)]


def get_received_messages_by_id(user_id):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT messages.*, users.username as sender_username
        FROM users
        INNER JOIN messages ON messages.sender_id = users.id
        WHERE messages.receiver_id = %s AND messages.message_type = 'Received';
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    return rows


def get_user_by_sessid(sessid) -> int:
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM USERS WHERE SESSID = %s", sessid)
    return cursor.fetchone()


def get_sent_messages_by_id(id):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT messages.*, users.username as sender_username
        FROM users
        INNER JOIN messages ON messages.sender_id = users.id
        WHERE messages.sender_id = id = %s AND messages.message_type = 'Received';
        """,
        (id,)
    )
    rows = cursor.fetchall()
    return rows

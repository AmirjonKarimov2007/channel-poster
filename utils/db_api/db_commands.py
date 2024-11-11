import asyncpg
from asyncpg import Connection, Record
from asyncpg.pool import Pool
from typing import Union

from data import config
from datetime import datetime

class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
            port=config.DB_PORT,
        )

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result


    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${index + 1}" for index, item in enumerate(parameters)
        ])
        return sql, tuple(parameters.values())

    async def stat(self):
        return await self.execute(f"SELECT COUNT(*) FROM users_user;", fetchval=True)

    async def add_admin(self, user_id: str, full_name: str):
        sql = """
            INSERT INTO Admins( user_id, full_name ) VALUES($1, $2)
            """
        await self.execute(sql, user_id, full_name, execute=True)
        
    async def is_user(self, **kwargs):
        sql = "SELECT * FROM users_user WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        # Convert user_id to integer
        parameters = tuple(int(param) if param == 'user_id' else param for param in parameters)

        return await self.execute(sql, *parameters, fetch=True)
    async def add_user(self, name, username, user_id):
        sql = """
            INSERT INTO users_user (name, username, user_id)
            VALUES($1, $2, $3)
            RETURNING *
        """
        return await self.execute(sql, name, username, user_id, fetchrow=True)


    async def is_admin(self, **kwargs):
        sql = "SELECT * FROM Admins WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        # Convert user_id to string
        parameters = tuple(str(param) for param in parameters)

        return await self.execute(sql, *parameters, fetch=True)

    async def select_all_users(self):
        sql = """
        SELECT * FROM users_user
        """
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM users_user WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return await self.execute(sql, *parameters, fetch=True)

    async def count_users(self):
        return await self.execute("SELECT COUNT(*) FROM users_user;", fetchval=True)
    
    async def delete_users(self):
        await self.execute("DELETE FROM users_user", execute=True)

    async def create_table_files(self):
        sql = """
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            type TEXT,
            file_id TEXT,
            caption TEXT,
            user_id INTEGER
            );
        """
        await self.execute(sql, execute=True)

    async def add_files(self, type: str=None, file_id: str=None, caption: str = None, user_id: str =None):
        sql = """
        INSERT INTO files(type, file_id, caption, user_id) VALUES($1, $2, $3, $4)
        """
        await self.execute(sql, type, file_id, caption, user_id, execute=True)

    async def select_files(self, **kwargs):
        sql = " SELECT * FROM files WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return await self.execute(sql, *parameters, fetch=True)

    async def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL UNIQUE ,
            full_name TEXT
            );
        """
        await self.execute(sql, execute=True)

    async def add_admin(self, user_id: int, full_name: str):
        sql = """
            INSERT INTO Admins( user_id, full_name ) VALUES($1, $2)
            """
        await self.execute(sql, user_id, full_name, execute=True)

    async def select_all_admins(self):
            sql = """
            SELECT * FROM Admins
            """
            return await self.execute(sql, fetch=True)



        
    async def is_admin(self, **kwargs):
        sql = "SELECT * FROM Admins WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return await self.execute(sql, *parameters, fetch=True)

    async def select_all_admin(self, **kwargs):
            sql = "SELECT * FROM Admins WHERE "
            sql, parameters = self.format_args(sql, kwargs)

            return await self.execute(sql, *parameters, fetch=True)
        
    async def stat_admins(self):
        return await self.execute(f"SELECT COUNT(*) FROM Admins;", fetchval=True)

    async def delete_admin(self, admin_id):
        await self.execute("DELETE FROM Admins WHERE user_id=$1", admin_id, execute=True)

    async def select_admins(self):
        sql = "SELECT * FROM Admins WHERE TRUE"
        return await self.execute(sql, fetch=True)

        return await self.execute(sql, *parameters, fetch=True)

    async def create_table_channel(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Channels (
            id SERIAL PRIMARY KEY,
            channel TEXT
            );
        """
        await self.execute(sql, execute=True)

    async def add_channel(self, channel: str):
        sql = """
            INSERT INTO Channels(channel) VALUES($1)
            """
        await self.execute(sql, channel, execute=True)

    async def check_channel(self, channel):
        return await self.execute("SELECT channel FROM Channels WHERE channel=$1", channel, fetchval=True)
    async def channel_stat(self):
        return await self.execute(f"SELECT COUNT(*) FROM Channels;", fetchval=True)

    async def select_channels(self):
        return await self.execute("SELECT * FROM Channels", fetch=True)

    async def select_all_channels(self):
        return await self.execute("SELECT * FROM Channels", fetch=True)

    async def delete_channel(self, channel):
        return await self.execute("DELETE FROM Channels WHERE channel=$1", channel, execute=True)




    # Postlar bo'yicha funksiyalar
    async def select_all_posts(self):
        sql = """
        SELECT * FROM users_Post
        """
        return await self.execute(sql, fetch=True)
    async def select_post(self, **kwargs):
        sql = "SELECT * FROM users_Post WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return await self.execute(sql, *parameters, fetch=True)

    async def select_post_nomzodlar(self, post_id):
        sql_with_nomzodlar = """
        SELECT p.id, p.title, p.channel, p.message_id, p.created_date, p.end_date,
               n.id AS nomzod_id, n.fullname, n.ovozlar
        FROM users_post AS p
        LEFT JOIN users_post_nomzodlar AS pn ON p.id = pn.post_id
        LEFT JOIN users_nomzodlar AS n ON n.id = pn.nomzodlar_id
        WHERE p.id = $1;
        """

        sql_post_only = """
        SELECT p.id, p.title, p.channel, p.message_id, p.created_date, p.end_date
        FROM users_post AS p
        WHERE p.id = $1;
        """

        result = await self.execute(sql_with_nomzodlar, post_id, fetch=True)

        if not result or all(r['nomzod_id'] is None for r in result):
            post_info = await self.execute(sql_post_only, post_id, fetch=True)
            return post_info

        return result

    async def select_nomzot(self, **kwargs):
        sql = "SELECT * FROM users_Nomzodlar WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return await self.execute(sql, *parameters, fetch=True)

    async def update_nomzot_vote(self, ovozlar, id):
        sql = "UPDATE users_Nomzodlar SET ovozlar=$1 WHERE id=$2"
        return await self.execute(sql, ovozlar, id, execute=True)

    async def add_vote(self, telegram_id, nomzod_id, post_id):
        sql = """
            INSERT INTO users_nomzot_ovozlar (telegram_id, nomzod_id, post_id)
            VALUES($1, $2, $3)
            RETURNING *
        """
        return await self.execute(sql, telegram_id, nomzod_id, post_id, fetchrow=True)

    async def select_all_votes(self, post_id):
        sql = """
        SELECT * FROM users_Nomzot_Ovozlar
        WHERE post_id = $1
        """
        return await self.execute(sql, post_id, fetch=True)

    async def update_post_message_id_and_channel(self, message_id, channel, id):
        sql = "UPDATE users_Post SET message_id = $1, channel = $2 WHERE id = $3"
        return await self.execute(sql, message_id, channel, id, execute=True)



# Post uchun Handlerlar

    async def add_post(self, title, channel, message_id,pin=False, created_date=None, nomzodlar=None, end_date=None):
        if not created_date:
            created_date = datetime.now()
        sql = """
            INSERT INTO users_post (title, channel, message_id,pin, created_date, end_date)
            VALUES ($1, $2, $3, $4, $5,$6)
            RETURNING id
        """
        return await self.execute(sql, title, channel, message_id,pin, created_date, end_date, fetchrow=True)

    async def delete_post_with_nomzodlar_and_votes(self, post_id):
        try:
            # 1. Bog'liq post-nomzodlar bog'lanishini o'chirish
            sql_delete_post_nomzodlar = "DELETE FROM users_post_nomzodlar WHERE post_id = $1"
            await self.execute(sql_delete_post_nomzodlar, post_id, execute=True)

            # 2. Bog'liq ovozlarni o'chirish
            sql_delete_votes = "DELETE FROM users_nomzot_ovozlar WHERE post_id = $1"
            await self.execute(sql_delete_votes, post_id, execute=True)

            # 3. Bog'liq nomzodlarni o'chirish
            sql_delete_nomzodlar = "DELETE FROM users_nomzodlar WHERE posts_id = $1"
            await self.execute(sql_delete_nomzodlar, post_id, execute=True)

            # 4. Postni o'chirish
            sql_delete_post = "DELETE FROM users_Post WHERE id = $1"
            return await self.execute(sql_delete_post, post_id, execute=True)

        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")
            return None

# Pin postdagi db funksiyalar
    async def add_post(self, title, channel, message_id, created_date=None, nomzodlar=None, end_date=None):
        if not created_date:
            created_date = datetime.now()
        sql = """
            INSERT INTO users_post (title, channel, message_id, created_date, end_date)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        return await self.execute(sql, title, channel, message_id, created_date, end_date, fetchrow=True)
    async def update_post_checkbox(self, pin, id):
        sql = "UPDATE users_Post SET pin=$1 WHERE id=$2"
        return await self.execute(sql, pin, id, execute=True)

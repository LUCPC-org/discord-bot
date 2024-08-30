import os

import aiosqlite

DATABASE_PATH = (
    f"{os.path.realpath(os.path.dirname(__file__))}/../database/database.sqlite"
)


class UserAlreadyExists(Exception):
    "Raised when the user is already on the leaderboard"

    def __init__(self) -> None:
        super().__init__("You are already on the leaderboard!")


class DatabaseManager:
    def __init__(self, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    async def add_user_to_leaderboard(self, user: dict):
        """
        This function will add a user to the leaderboard_entry table

        :param user: A dictionary representing all the values in the table (discord_id, kattis_username, original_points, current_points)
        """

        cursor = await self.connection.execute(
            "SELECT EXISTS(SELECT 1 FROM leaderboard_entry WHERE discord_id = ?)",
            (user["discord_id"],),
        )
        (exists,) = await cursor.fetchone()

        if exists:
            # not sure if i needed to do this or not
            await cursor.close()
            raise UserAlreadyExists()

        await self.connection.execute(
            "INSERT INTO leaderboard_entry(discord_id, kattis_username, original_points, current_points) VALUES (?, ?, ?, ?)",
            (
                user["discord_id"],
                user["kattis_username"],
                user["original_points"],
                user["current_points"],
            ),
        )

        # Add the user to the score_snapshot table
        await self.insert_score_snapshot(user["discord_id"], user["current_points"])

        await self.connection.commit()

    async def get_leaderboard_entries(self) -> list[dict]:
        """
        returns a list of the leaderboard entries ordered by the difference of original_points and current_points
        """
        cursor = await self.connection.execute(
            "SELECT * FROM leaderboard_entry ORDER BY current_points - original_points DESC"
        )

        users = await cursor.fetchall()
        # Reformats the users list to be more readable
        users = [
            {
                "discord_id": user[0],
                "kattis_username": user[1],
                "original_points": user[2],
                "current_points": user[3],
            }
            for user in users
        ]
        return users

    async def update_leaderboard_entries(self, new_users) -> None:
        """
        takes in a list of users and updates the leaderboard entries with the list
        """
        for user in new_users:
            await self.connection.execute(
                "UPDATE leaderboard_entry SET current_points = ? WHERE discord_id = ?",
                (user["current_points"], user["discord_id"]),
            )

        await self.connection.commit()
    
    async def insert_score_snapshot(self, user_id: str, score: float) -> None:
        """
        This function will insert a score snapshot into the score_snapshot table

        It will also insert the correct date into the date column

        It will ignore the insert if the user_id and score already exist in the table
        """
        await self.connection.execute(
            "INSERT OR IGNORE INTO score_snapshot(discord_id, score, date) VALUES (?, ?, date('now'))",
            (user_id, score),
        )

        await self.connection.commit()

    async def does_user_exist(self, user_id: str) -> bool:
        """
        This function will return True if the user exists in the leaderboard_entry table
        """
        cursor = await self.connection.execute(
            "SELECT EXISTS(SELECT 1 FROM leaderboard_entry WHERE discord_id = ?)",
            (user_id,),
        )
        (exists,) = await cursor.fetchone()
        return exists
    
    async def get_user_scores_over_time(self, user_id: str) -> list[dict]:
        """
        This function will return a list of dictionaries where each dictionary contains the date and score of the user
        """
        cursor = await self.connection.execute(
            "SELECT * FROM score_snapshot WHERE discord_id = ? ORDER BY date ASC",
            (user_id,),
        )

        scores = await cursor.fetchall()
        scores = [
            {"date": score[2], "score": score[0]} for score in scores
        ]
        return scores
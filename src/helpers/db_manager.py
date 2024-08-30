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
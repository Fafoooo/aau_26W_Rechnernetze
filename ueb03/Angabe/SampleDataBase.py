"""Simple in-memory database for the POP3 lab."""

class SampleDataBase:
    def __init__(self):
        self.users = {
            "alice": {
                "password": "secret",
                "messages": [
                    {"id": 1, "raw":
                     "From: bob@example.com\r\n"
                     "To: alice@example.com\r\n"
                     "Subject: Welcome to the POP3 lab\r\n"
                     "Date: Tue, 22 Sep 2026 09:00:00 +0200\r\n"
                     "\r\nHello Alice,\r\n\r\nWelcome to the POP3 laboratory.\r\n\r\nBest,\r\nBob\r\n"},
                    {"id": 2, "raw":
                     "From: lecturer@example.com\r\n"
                     "To: alice@example.com\r\n"
                     "Subject: Network Programming Exercise\r\n"
                     "Date: Tue, 22 Sep 2026 10:15:00 +0200\r\n"
                     "\r\nPlease remember to test your POP3 client and server.\r\n"},
                    {"id": 3, "raw":
                     "From: team@example.com\r\n"
                     "To: alice@example.com\r\n"
                     "Subject: Meeting tomorrow\r\n"
                     "Date: Tue, 22 Sep 2026 11:30:00 +0200\r\n"
                     "\r\nThe meeting starts at 10:00 tomorrow.\r\n"},
                    {"id": 4, "raw":
                     "From: admin@example.com\r\n"
                     "To: alice@example.com\r\n"
                     "Subject: POP3 server test\r\n"
                     "Date: Tue, 22 Sep 2026 12:00:00 +0200\r\n"
                     "\r\nThis message is used to test the RETR command.\r\n"},
                ]
            }
        }

    def authenticate(self, username, password):
        user = self.users.get(username)
        return user is not None and user["password"] == password

    def get_messages(self, username):
        user = self.users.get(username)
        return [] if user is None else user["messages"]

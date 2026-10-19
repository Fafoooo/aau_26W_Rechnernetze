## Available Functions

### `authenticate(username, password)`

Authenticates a user.

**Parameters:**

- `username` (`str`) – username (alice)
- `password` (`str`) – password (secret)

**Returns:**

- `True` if authentication succeeds
- `False` if authentication fails

**Example:**

```python
success = db.authenticate("alice", "alice123")
```

---

### `get_messages(username)`

Returns all messages belonging to the specified user.

**Parameters:**

- `username` (`str`) – username

**Returns:**

A `list[dict]` containing the user's messages.

Each message dictionary contains:

- `id` (`int`) – message number
- `raw` (`str`) – complete email including headers and body

If the user does not exist or has no messages, an empty list is returned.

**Example:**

```python
messages = db.get_messages("alice")

for message in messages:
    print(message["id"])
    print(message["raw"])
```

## Complete Example

```python
from SampleDataBase import SampleDataBase


db = SampleDataBase()

username = "alice"
password = "alice123"

if db.authenticate(username, password):
    print("Login successful")

    messages = db.get_messages(username)

    print(f"Number of messages: {len(messages)}")

    for message in messages:
        print(f"Message {message['id']}")
        print(message["raw"])
        print("-" * 40)
else:
    print("Login failed")
```

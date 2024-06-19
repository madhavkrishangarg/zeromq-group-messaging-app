# ZeroMQ Group Messaging Application

## Components
1. **Message Server**: Maintains the list of groups and handles user requests to get the list of live groups.
2. **Groups**: Manage users, handle message storage, and facilitate communication within the group.
3. **Users**: Interact with groups to join/leave, send messages, and retrieve messages.

## Prerequisites
- Python 3.x
- ZeroMQ library (`pyzmq`)
```sh
$ python3 -m pip install pyzmq
```
We need to change the IP addresses of server.py, group.py and user.py because every time the VM instance restarts, the external IP address of instances change:
Change line 18 and 131 in group.py
change line 33,34,52 and 66 in user.py

A group can hold maximum of 14 users concurrently

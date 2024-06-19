pre-requisite:

$ python3 -m pip install pyzmq

We need to change the IP addresses of server.py, group.py and user.py because every time the VM instance stops and starts again the external IP address of instance change

Change line 18 and 131 in group.py
change line 33,34,52 and 66 in user.py

A group can hold maximum of 14 users concurrently

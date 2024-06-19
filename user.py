import json
import threading
import zmq
import uuid
import time
from datetime import datetime

user_name=str(uuid.uuid1())
joined_groups={}
group_list={}

context = zmq.Context()
socket = context.socket(zmq.REQ)
try:
    port = socket.bind_to_random_port('tcp://*', min_port=1000, max_port=7000, max_tries=500)
except Exception as e:
    print(f"Could not bind server to a port: {e}")

while 1:
    print("1: get list of active groups")
    print("2: join a group")
    print("3: send a message")
    print("4: fetch all message from a group")
    print("5: leave a group")
    print("6: exit")
    choice = int(input())

    socket.setsockopt(zmq.LINGER, 0)
    socket.close()
    socket = context.socket(zmq.REQ)

    if choice == 1:
        socket.connect("tcp://34.131.145.245:2000")
        request=json.dumps({"method":"get_group_list","args":{"ip":"34.30.6.191","port":port}})
        socket.send(request.encode('utf-8'),zmq.NOBLOCK)
        if (socket.poll(5000) and zmq.POLLIN) != 0:
            msg = json.loads(socket.recv().decode('UTF-8'))
            print(msg)
            if(msg["status"]==1):
                # group_list=msg["servers"]
                servers = msg["servers"]
                print(servers)      #servers is a list of dictionaries
                for server in servers:
                    print(server["name"], server["address"])
                    group_list[server["name"]] = server["address"]
            else:
                print("(-) unable to get list of active groups")

        else:
            print("(-) unable to connect to server")
            exit(1)
        socket.disconnect("tcp://34.131.145.245:2000")


    if choice == 2:
        print("List of servers:")
        for group in group_list:
            print(group, group_list[group])
            
        choice = input("enter the group name that you want to join: ")
        try:
            CONN = f"tcp://{group_list[choice]}"
            print("pinging group", CONN)
            socket.connect(CONN)
            
            message = {"args": {"ip": "34.30.6.191", "port": port, "name": user_name}, "method": "join_group"}
            socket.send(json.dumps(message).encode('UTF-8'), zmq.NOBLOCK)
            # socket.send_multipart([user_name.encode('utf-8'), json.dumps(message).encode('utf-8')]) 

            
            if (socket.poll(5000)) != 0:
                # parts = socket.recv_multipart()
                # print(parts)
                # res=json.loads(parts[-1].decode('utf-8'))
                res = json.loads(socket.recv().decode('UTF-8'))
                print(res["status"])
                if (res["status"] == 1):
                    joined_groups[choice] = group_list[choice]
                    print(f"(+) Joined group {choice}")
                print(joined_groups)
            else:
                print("(-) Server seems to be offline.\nFAIL.")
            socket.disconnect(CONN)
        except:
            print("(-) Could not connect to the server")
            
#implement 3,4,5

    if choice == 3:
        text=input("Enter the message: ")
        group=input("Enter the group name: ")
        if group not in joined_groups:
            print("(-) You are not a part of this group")
            continue
        try:
            CONN = f"tcp://{joined_groups[group]}"
            print("pinging group", CONN)
            socket.connect(CONN)
            message = {
                "method": "send_message",
                "args": {
                    "name": user_name,
                    "text": text
                }
            }
            # socket.send_multipart([user_name.encode('utf-8'), json.dumps(message).encode('utf-8')]) 
            socket.send(json.dumps(message).encode('UTF-8'))

            if (socket.poll(5000) & zmq.POLLIN) != 0:
                # parts = socket.recv_multipart()
                # print(parts)
                # res=json.loads(parts[-1].decode('utf-8'))
                res = json.loads(socket.recv().decode('UTF-8'))
                print(res["status"])
                if (res["status"] == 1):
                    print(f"(+) Message sent to group {group}")
            else:
                print("(-) Server seems to be offline.\nFAIL.")
        except:
            print("(-) Could not connect to the server")
        


    if choice == 4:
        group=input("Enter the group name: ")
        timestamp = input("Enter the timestamp (HH:MM:SS) : ").strip()      #check the functionality of timestamp
        if timestamp:
            current_date = datetime.now().date()
            given_time = datetime.strptime(timestamp, '%H:%M:%S')
            combined_datetime = datetime.combine(current_date, given_time.time())
            timestamp = combined_datetime.timestamp()
        else:
            timestamp = 0
        
        if group not in joined_groups:
            print("(-) You are not a part of this group")
            continue
        try:
            CONN = f"tcp://{joined_groups[group]}"
            print("pinging group", CONN)
            socket.connect(CONN)
            message = {
                "method": "get_messages",
                "args": {
                    "name": user_name,
                    "timestamp": timestamp
                }
            }
            print(message)
            # socket.send_multipart([user_name.encode('utf-8'), json.dumps(message).encode('utf-8')]) 
            socket.send(json.dumps(message).encode('UTF-8'))
            if (socket.poll(5000) & zmq.POLLIN) != 0:
                res = json.loads(socket.recv().decode('UTF-8'))
                # parts = socket.recv_multipart()
                # print(parts)
                # res=json.loads(parts[-1].decode('utf-8'))
                print(res["status"])
                if (res["status"] == 1):
                    print(f"(+) Messages received from group {group}")
                    # print(res["messages"])
                    for dict in res["messages"]:
                        print(f"{dict['sender']}: {dict['text']} at {dict['time']}")
                
            else:
                print("(-) Server seems to be offline.\nFAIL.")
        except:
            print("(-) Could not connect to the server")

    if choice == 5:
        group=input("Enter the group name: ")
        msg = {
            "method": "leave_group",
            "args": {
                "name": user_name
            }
        }
        try:
            CONN = f"tcp://{joined_groups[group]}"
            print("pinging group", CONN)
            socket.connect(CONN)
            socket.send(json.dumps(msg).encode('UTF-8'))
            if (socket.poll(5000) & zmq.POLLIN) != 0:
                res = json.loads(socket.recv().decode('UTF-8'))
                # parts = socket.recv_multipart()
                # print(parts)
                # res=json.loads(parts[-1].decode('utf-8'))
                print(res["status"])
                if (res["status"] == 1):
                    print(f"(+) Left group {group}")
                    del joined_groups[group]
            else:
                print("(-) Server seems to be offline.\nFAIL.")
        except:
            print("(-) Could not connect to the server")
    
    if choice == 6:
        exit(0)
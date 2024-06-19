import zmq
import json
from datetime import datetime
import uuid
import time
import threading

name = str(uuid.uuid1())
usertele = {}
messages = []
threads=[]

def add_message(sender, text):
    messages.append({"sender": sender, "text": text, "time": datetime.now()})
    messages.sort(key=lambda x: x["time"])

def register_to_server(socket, port):
    request = {"method": "register_to_server", "args": {"name": name, "ip": "35.193.60.249", "port": port}}
    socket.send(json.dumps(request).encode('utf-8'))
    response = socket.recv()
    res = json.loads(response.decode('utf-8'))
    print(f"Server registration response: {res}")
    print(f"Server registration status: {res['status']}")
    return res["status"]

def handle_user_request(port):
    context = zmq.Context()
    user_socket = context.socket(zmq.REP)
    user_socket.bind(f"tcp://*:{port}")
    print(f"User socket running on port {port}")
    while True:
        try:
            msg = json.loads(user_socket.recv().decode('utf-8'))
            if msg["method"].lower() == "join_group":
                args = msg["args"]
                print(f"JOIN REQUEST FROM {args['name']} [uuid]")
                try:
                    user_address = f"{args['ip']}:{args['port']}"
                    user_uuid = args['name']
                    if user_uuid in usertele:
                        # if user already exists
                        print(f"(-) user uuid {user_uuid} already exists")
                        user_socket.send(json.dumps({"status": 0}).encode('utf-8'))
                    else:
                        # if user does not exist
                        usertele[user_uuid] = user_address
                        print(f"(+) user: {user_uuid} registered at {user_address}")
                        user_socket.send(json.dumps({"status": 1}).encode('utf-8'))
                            # threads.append(threading.Thread(target=handle_user_request))
                            # threads[-1].start()

                except Exception as e:
                    print(f"(-) Error in registering group {user_uuid}: {e}")
                    user_socket.send(json.dumps({"status": 0}).encode('utf-8'))
                    msg = json.loads(user_socket.recv().decode('utf-8'))
            
            
            if msg["method"].lower() == "leave_group":
                args = msg["args"]
                print(f"LEAVE REQUEST FROM {args['name']} [uuid]")
                try:
                    user_uuid = args['name']
                    if user_uuid in usertele:
                        # if user already exists
                        usertele.pop(user_uuid)
                        print(f"(+) user: {user_uuid} left the group")
                        user_socket.send(json.dumps({"status": 1}).encode('utf-8'))
                    else:
                        # if user does not exist
                        print(f"(-) user uuid {user_uuid} does not exist")
                        user_socket.send(json.dumps({"status": 0}).encode('utf-8'))
                except Exception as e:
                    print(f"(-) Error in leaving group {user_uuid}: {e}")
                    user_socket.send(json.dumps({"status": 0}).encode('utf-8'))


            if msg["method"].lower() == "get_messages":
                args = msg["args"]
                print(f"GET MESSAGES FROM {args['name']} [uuid]")
                try:
                    user_uuid = args['name']
                    if user_uuid in usertele:
                        # if user already exists
                        print(f"(+) user: {user_uuid} requested messages")
                        timestamp = args.get("timestamp", 0)
                        # Convert datetime objects to formatted strings
                        res = [{"sender": i["sender"], "text": i["text"], "time": i["time"].strftime("%d/%m/%Y %H:%M:%S")}
                               for i in messages if i["time"].timestamp() >= timestamp]
                        user_socket.send(json.dumps({"status": 1, "messages": res}).encode('utf-8'))
                    else:
                        # if user does not exist
                        print(f"(-) user uuid {user_uuid} does not exist")
                        user_socket.send(json.dumps({"status": 0}).encode('utf-8'))
                except Exception as e:
                    print(f"(-) Error in getting messages from {user_uuid}: {e}")
                    user_socket.send(json.dumps({"status": 0}).encode('utf-8'))

            if msg["method"].lower() == "send_message":
                args = msg["args"]
                print(f"SEND MESSAGE FROM {args['name']} [uuid]")
                try:
                    user_uuid = args['name']
                    if user_uuid in usertele:
                        # if user already exists
                        print(f"(+) user: {user_uuid} sent a text")
                        add_message(user_uuid, args["text"])
                        user_socket.send(json.dumps({"status": 1}).encode('utf-8'))
                    else:
                        # if user does not exist
                        print(f"(-) user uuid {user_uuid} does not exist")
                        user_socket.send(json.dumps({"status": 0}).encode('utf-8'))
                except Exception as e:
                    print(f"(-) Error in sending text from {user_uuid}: {e}")
                    user_socket.send(json.dumps({"status": 0}).encode('utf-8'))

        except zmq.error.Again:  # Handle non-blocking socket read
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Error handling client: {e}")
            # user_socket.close()
            break
        
port = 2008
context = zmq.Context.instance()
request_socket = context.socket(zmq.REQ)
# user_socket = context.socket(zmq.REP)

print(f"Server running on port {port}")

request_socket.connect("tcp://34.131.145.245:2000")      #connect to host
if not register_to_server(request_socket, port):
    print("Could not register the server. Exiting.")
    # user_socket.close()
    exit(1)

request_socket.close()

# user_socket.bind(f"tcp://*:{port}")

for i in range(14):     
    threads.append(threading.Thread(target=handle_user_request, args=(port+i,)))
    threads[-1].start()
    
# handle_user_request()
import json
import threading
import zmq
import uuid
import time
from datetime import datetime

port=2000
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://*:{port}")

servers={}

print(f"(+) Server running on port {port}")

while 1:
    msg=socket.recv()
    msg=json.loads(msg)
    print(f"Received request: {msg}")
    
    if(msg["method"].lower()=="register_to_server"):
        args=msg["args"]
        print(f"""JOIN REQUEST FROM {args["ip"]}:{args["port"]} [IP: PORT]""")
        try:
            group_address=f"{args['ip']}:{args['port']}"
            # print(type(args['ip']), type(args['port']))
            group_address_list=[args['ip'],args['port']]
            group_name=args['name']
            if(group_name in servers):
                print(f"(-) Group name {group_name} already exists")
                socket.send(json.dumps({"status":0}).encode('utf-8'))
            else:
                servers[group_name]=group_address_list
                print(f"(+) Group {group_name} registered at {group_address}")
                socket.send(json.dumps({"status":1}).encode('utf-8'))
        except:
            print(f"(-) Error in registering group {group_name}")
            socket.send(json.dumps({"status":0}).encode('utf-8'))
    
    
    if(msg["method"].lower()=="get_group_list"):
        args=msg["args"]
        print(f"GET GROUP LIST REQUEST from {args['ip']}:{args['port']}")
        group_list=[]
        try:
            if(len(servers)==0):
                print("(-) No groups registered")        
            else:    
                for group_name in servers:
                    servers[group_name][-1]+=1
                    group_ip, group_port = servers[group_name]
                    addr=f"{group_ip}:{group_port}"
                    group_list.append({"name":group_name,"address":addr})
            socket.send(json.dumps({"status":1,"servers":group_list}).encode('utf-8'))
        except:
            print(f"(-) Error in getting group list")
            socket.send(json.dumps({"status":0,"servers":group_list}).encode('utf-8'))
    
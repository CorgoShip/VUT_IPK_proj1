#!/usr/bin/env python3

import socket
import re
import sys

HOST = '127.0.0.1'           # Standard loopback interface address (localhost)
PORT = sys.argv[1]        # Port to listen on (non-privileged ports are > 1023)

def respond(name, typ):
    if ((re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", name) == None) and typ == "A"):
        try:
            ip = socket.gethostbyname(name)
            response = name + ":" + typ + "=" + ip + "\r\n"
            conn.sendall(bytes("HTTP/1.1 200 OK \r\n\r\n" + response, "utf-8"))
        except:
            conn.sendall(bytes("HTTP/1.1 404 Not Found \r\n\r\n", "utf-8"))
    elif ((re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", name) != None) and typ == "PTR"):
        try:
            ip = socket.gethostbyaddr(name)[0]
            response = name + ":" + typ + "=" + ip + "\r\n"
            conn.sendall(bytes("HTTP/1.1 200 OK \r\n\r\n" + response, "utf-8"))
        except:
            conn.sendall(bytes("HTTP/1.1 404 Not Found \r\n\r\n", "utf-8"))
    else:
        conn.sendall(bytes("HTTP/1.1 400 Bad Request \r\n\r\n", "utf-8"))

def postRespond(arglist):
    goodResp = False
    response = "HTTP/1.1 200 OK \r\n\r\n"
    for line in arglist:
        try:
            name = line.split(':')[0].strip()
            typ = line.split(':')[1].strip()
            if ((re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", name) == None) and typ == "A"):
                try:
                    ip = socket.gethostbyname(name)
                    response += name + ":" + typ + "=" + ip + "\r\n"
                    goodResp = True
                except:
                    pass
            elif ((re.search("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", name) != None) and typ == "PTR"):
                try:
                    ip = socket.gethostbyaddr(name)[0]
                    response += name + ":" + typ + "=" + ip + "\r\n"
                    goodResp = True
                except:
                    pass
            else:
                pass
        except:
            conn.sendall(bytes("HTTP/1.1 400 Bad Request \r\n\r\n", "utf-8"))
            return        
    if goodResp:
        conn.sendall(bytes(response, "utf-8"))
    else:
        conn.sendall(bytes("HTTP/1.1 404 Not Found \r\n\r\n", "utf-8"))

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, int(PORT)))
            s.listen()
            conn, addr = s.accept()
        except:
            print("Spatny port, port musi byt v rozsahu 1024-65535")
            exit(1)        
        with conn:
            data = conn.recv(1024)
            string = data.decode("utf-8")
            lines = string.splitlines()

            operation = lines[0].split()[0]
            args = lines[0].split()[1]

            if operation == "GET":
                req = args.split('?')[0]
                if req == "/resolve":
                    try:
                        if (args.split('?')[1].split('&')[0].split('=')[0] == "name" and args.split('?')[1].split('&')[1].split('=')[0] == "type"):
                            name = args.split('?')[1].split('&')[0].split('=')[1]
                            typ = args.split('?')[1].split('&')[1].split('=')[1]
                            respond(name, typ)
                        elif (args.split('?')[1].split('&')[0].split('=')[0] == "type" and args.split('?')[1].split('&')[1].split('=')[0] == "and"):
                            name = args.split('?')[1].split('&')[1].split('=')[1]
                            typ = args.split('?')[1].split('&')[0].split('=')[1]
                            respond(name, typ)
                        else:
                            conn.sendall(bytes("HTTP/1.1 400 Bad Request \r\n\r\n", "utf-8"))
                    except:
                        conn.sendall(bytes("HTTP/1.1 400 Bad Request \r\n\r\n", "utf-8"))                    
                elif req == "/dns-query":                    
                    conn.sendall(bytes("HTTP/1.1 405 Method Not Allowed \r\n\r\n", "utf-8"))
                else:
                    conn.sendall(bytes("HTTP/1.1 400 Bad Request \r\n\r\n", "utf-8"))
            elif operation == "POST":
                if lines[0].split()[1] == "/dns-query":
                    body = string.split("\r\n\r\n")
                    arglist = body[1].splitlines()
                    postRespond(arglist)
                elif lines[0].split()[1] == "/resolve":
                    conn.sendall(bytes("HTTP/1.1 405 Method Not Allowed \r\n\r\n", "utf-8"))                    
                else:
                    conn.sendall(bytes("HTTP/1.1 400 Bad Request \r\n\r\n", "utf-8"))                
            else:
                conn.sendall(bytes("HTTP/1.1 405 Method Not Allowed \r\n\r\n", "utf-8"))

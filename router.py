sockets = []

def addConnection(socket):
	sockets.append(socket)

def removeConnection(socket):
	sockets.remove(socket)

def numberOfConnections():
	return len(sockets)

def route(socket,message):
	for x in sockets:
		if x != socket:
			x.write_message(message)

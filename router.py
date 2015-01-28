import networkx as nx
import json

userRootNode = 'userRootNode'
topicRootNode = 'topicRootNode'

# g stores connections between users and topics with
# one node for each user and one node for each topic and one node for each socket.
# Users are accessed by getting neighbors of the userRootNode
# Topics are accessed by getting neighbors of the topicRootNode
# An edge between a socket and a topic indicates a subscription

g = nx.Graph()
g.add_node(userRootNode)
g.add_node(topicRootNode)




topicPrefix = 'topic.'
def topicNameToLabel(topicName):
	return topicPrefix + topicName

def topicLabelToName(topicLabel):
	return topicLabel.partition(topicPrefix)[2]

userPrefix = 'user.'
def userNameToLabel(userName):
	return userPrefix + userName

def userLabelToName(userLabel):
	return userLabel.partition(userPrefix)[2]



# Function decorator for returning if message is empty
def returnOnEmpty(func):
	def decorated(socket, argument, payload):
		if(argument == ''):
			print 'No argument supplied to function'
			return
		else:
			func(socket, argument, payload)
	return decorated



# Generates a message listing available commands and sends it to the user
def commandHelp(socket, *_):
	iteratorList = zip(commands.iterkeys(),commands.itervalues())
	helpList = ["%-10s %s" % (x[0],x[1]['helpString']) for x in iteratorList]
	helpList.sort()
	socket.write_message("\n".join(helpList))


def getUserLabel(socket):
	try:
		return list(nx.common_neighbors(g, socket, userRootNode))[0]
	except (nx.NetworkXError, IndexError):
		return None

def getUserName(socket):
	userLabel = getUserLabel(socket)
	if userLabel is None:
		return None
	else:
		return userLabelToName(userLabel)


# Sets a new username or returns the current username
def commandName(socket, newUserName, *_):
	newUserName = str(newUserName)

	if(newUserName == ''):
		userName = getUserName(socket)
		if userName is None:
			socket.write_message('You haven\'t set have a username yet')
		else:
			socket.write_message('Your username: ' + userName)
		
			
	else:
		newUserLabel = userNameToLabel(newUserName)
		# Check that the new name is not already in use
		if newUserLabel not in g:
			# Remove the old user name node if there was one
			oldUserLabel = getUserLabel(socket)
			if oldUserLabel is not None:
				g.remove_node(oldUserLabel)
				pikaClient.unbind_client_queue(oldUserLabel)


			# Add nodes and edges to routing graph
			g.add_edge(newUserLabel, socket)
			g.add_edge(newUserLabel, userRootNode)

			# Add RabbitMQ bindings
			pikaClient.bind_client_queue(newUserLabel)

			# Acknowledge to user that the name change succeeded
			socket.write_message('Your new username: ' + newUserName)
		else:
			socket.write_message("Username \'%s\' is not available" % newUserName)

def getUsers():
	userLabels = g[userRootNode]
	userNames = [userLabelToName(x) for x in userLabels]
	return userNames

def getTopics():
	topicLabels = g[topicRootNode]
	topicNames = [topicLabelToName(x) for x in topicLabels]
	return topicNames

def getUserTopicsLabels(socket):
	topicLabels = sorted(nx.common_neighbors(g, socket, topicRootNode))
	return topicLabels

def getTopicUsers(socket, topicName):
	userNames = []
	topicLabel = topicNameToLabel(topicName)

	if topicLabel in g:
		sockets = [x for x in g[topicLabel]]
		sockets.remove('topicRootNode')

		for x in sockets:
			userName = getUserName(socket)
			if userName is not None:
				userNames.append(userName)

	return userNames


# Returns a list of all users
def commandListUsers(socket, *_):
	rabbitSendServerMessage('Send a list of all usernames on this server')
	listResponse(socket, getUsers(), "There are 0 named users")

# Returns a list of all topics
def	commandListTopics(socket, *_):
	rabbitSendServerMessage('Send a list of all topics on this server')
	listResponse(socket, getTopics(), "There are 0 topics")

# Returns a list of all users subscribing to a topic
def commandListTopicUsers(socket, topicName, *_):
	rabbitSendServerMessage('Send a list of all usernames on this server subscribed to the topic ' + topicName)
	listResponse(socket, getTopicUsers(socket, topicName), 'This topic has 0 subscribers')

# Returns a list of all topics the user is subscribing to
def commandGetTopics(socket, *_):
	topicLabels = getUserTopicsLabels(socket)
	topicNames = [topicLabelToName(x) for x in topicLabels]
	listResponse(socket, topicNames, "You subscribe to 0 topics")

# Helper function that produces the message string and sends it through the socket
def listResponse(socket, nodeList, emptyResponse):
	response = emptyResponse
	if nodeList is not None:
		response = ["%s" % x for x in nodeList]
		response.sort()
		response = "\n".join(response)

		if response == '':
			response = emptyResponse

	socket.write_message(response)


# Called to subscribe to a topic
@returnOnEmpty
def commandSubscripeToTopic(socket, topicName, *_):
	topicLabel = topicNameToLabel(topicName)

	# Add edge between socket and topic
	g.add_edge(socket, topicLabel)

	# Add edge between topic and topicRootNode
	g.add_edge(topicLabel, topicRootNode)

	# Update RabbitMQ bindings
	pikaClient.bind_client_queue(topicLabel)


def unsubscribe(socket, topicLabel, *_):
	g.remove_edge(socket, topicLabel)

	# Topic node is always connected to topicRootNode so degree>=1 always 
	if(g.degree(topicLabel) < 2):
		# Remove topic if no sockets subscribe to it
		g.remove_node(topicLabel)

		# Update RabbitMQ bindings
		pikaClient.unbind_client_queue(topicLabel)


# Called to unsubscribe to a topic
@returnOnEmpty
def commandUnsubscripeToTopic(socket, topicName, *_):
	topicLabel = topicNameToLabel(topicName)

	# Remove edge between socket and topic
	if topicLabel in g and topicLabel in g[socket]:
		unsubscribe(socket, topicLabel)

	else:
		socket.write_message('You don\'t subscribe to that topic')

	

@returnOnEmpty
def commandPrivateMessage(socket, userName, message):
	rabbitSendClientMessage(socket, userNameToLabel(userName), message)

@returnOnEmpty
def commandTopicMessage(socket, topicName, message):
	rabbitSendClientMessage(socket, topicNameToLabel(topicName), message)

@returnOnEmpty
def commandSetAddressToUser(socket, userName, *_):
	socket.routing_key = userNameToLabel(userName)

@returnOnEmpty
def commandSetAddressToTopic(socket, topicName, *_):
	socket.routing_key = topicNameToLabel(topicName)




# A dictionary listing avaiable commands. Used to process input and generate help message
commandPrefix = '/'
commands = {
	commandPrefix+"h": 		{'function': commandHelp, 				'helpString': 'get info on commands'},
	commandPrefix+"n": 		{'function': commandName, 				'helpString': 'get name or set new name'},
	commandPrefix+"t": 		{'function': commandGetTopics, 			'helpString': 'list the topics you subscribe to'},
	commandPrefix+"ts": 	{'function': commandSubscripeToTopic, 	'helpString': 'subscribe to topic: /ts <topic>'},
	commandPrefix+"tu": 	{'function': commandUnsubscripeToTopic, 'helpString': 'unsubscribe to topic: /tu <topic>'},
	commandPrefix+"lu": 	{'function': commandListUsers, 			'helpString': 'list users'},
	commandPrefix+"lt": 	{'function': commandListTopics, 		'helpString': 'list topics'},
	commandPrefix+"ltu":	{'function': commandListTopicUsers, 	'helpString': 'list users in a specific topic: /ltu <topic>'},
	commandPrefix+"mu": 	{'function': commandPrivateMessage,		'helpString': 'send message to user: /mu <user> message'},
	commandPrefix+"mt": 	{'function': commandTopicMessage,		'helpString': 'send message to topic: /mt <topic> message'},
	commandPrefix+"au":		{'function': commandSetAddressToUser,	'helpString': 'set address to user: /au <user>'},
	commandPrefix+"at":		{'function': commandSetAddressToTopic,	'helpString': 'set address to topic: /at <topic>'}
}




def addConnection(socket):
	g.add_node(socket)
	socket.routing_key = None
	commandHelp(socket)

def removeConnection(socket):
	# Remove username node
	userLabel = getUserLabel(socket);
	if userLabel is not None:
		g.remove_node(userLabel)

		# Update RabbitMQ bindings
		pikaClient.unbind_client_queue(userLabel)

	# Remove subscriptions
	topicLabels = getUserTopicsLabels(socket)
	for x in topicLabels:
		unsubscribe(socket, x)
	
	# Remove socket node
	g.remove_node(socket)

	# TODO: Remove all topic nodes for which there are no longer any subscribers


def processWebSocketMessage(socket, message):
	print "MESSAGE: %s" % message
	data = json.loads(message)

	if 'command' in data:
		cmd = data['command']
		if cmd in commands:
			commands[cmd]['function'](socket, data['argument'], data['payload'])
		else:
			socket.write_message('Unrecognized command: ' + cmd)
	else:
		if socket.routing_key is not None:
			rabbitSendClientMessage(socket, socket.routing_key, data['payload'])
		else:
			socket.write_message("No address is set. See help (/h)")


def rabbitSendClientMessage(socket, routing_key, message):
	userName = getUserName(socket)
	if userName is None:
		socket.write_message("You must set a username before you can send messages")
	else:
		rabbitMessage = {
			'sender': userName,
			'payload': message
		}
		pikaClient.send_user_message(routing_key, json.dumps(rabbitMessage))



def rabbitProcessClientMessage(routing_key, message):
	try:
		iterator = g.neighbors_iter(routing_key)		
	except nx.NetworkXError:
		print 'Invalid routing key received'
		return

	data = json.loads(message)

	for x in iterator:
		if x is not userRootNode and x is not topicRootNode:
			x.write_message("%s: %s" % (data['sender'], data['payload']))


def rabbitSendServerMessage(message):
	rabbitMessage = {
		# 'sender': userName,
		'body': message
	}
	pikaClient.send_server_message(json.dumps(rabbitMessage))

def rabbitProcessServerMessage(routing_key, message):
	data = json.loads(message)
	print "SERVER_MESSAGE_RECEIVED: " + routing_key + message
		


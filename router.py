import networkx as nx

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
	def decorated(socket,message):
		if(message == ''):
			print 'Empty message'
			return
		else:
			func(socket,message)
	return decorated



# Generates a message listing available commands and sends it to the user
def commandHelp(socket, *_):
	iteratorList = zip(commands.iterkeys(),commands.itervalues())
	helpList = ["%-10s %s" % (x[0],x[1]['helpString']) for x in iteratorList]
	helpList.sort()
	socket.write_message("\n".join(helpList))


# Sets a new username or returns the current username
def commandName(socket, newUserName):
	if(newUserName == ''):
		try:
			userLabel = list(nx.common_neighbors(g, socket, userRootNode))[0]
			socket.write_message('Your username: ' + userLabelToName(userLabel))
		except (nx.NetworkXError, IndexError):
			socket.write_message('You haven\'t set have a username yet')
	else:
		newUserLabel = userNameToLabel(newUserName)
		# Check that the new name is not already in use
		if newUserLabel not in g:
			# Remove the old user name node if there was one
			try:
				nodes = list(nx.common_neighbors(g, socket, userRootNode))
				for node in nodes:
					g.remove_node(node) 
			except nx.NetworkXError:
				pass

			g.add_edge(newUserLabel, socket)
			g.add_edge(newUserLabel, userRootNode)

			# Acknowledge to user that the name change succeeded
			socket.write_message('Your new username: ' + newUserName)
		else:
			socket.write_message("Username \'%s\' is not available" % newUserName)


# Returns a list of all users
def commandGetUsersList(socket, *_):
	userLabels = g[userRootNode]
	userNames = [userLabelToName(x) for x in userLabels]
	listResponse(socket, userNames, "There are 0 named users")


# Returns a list of all topics
def	commandGetTopicsList(socket, *_):
	topicLabels = g[topicRootNode]
	topicNames = [topicLabelToName(x) for x in topicLabels]
	listResponse(socket, topicNames, "There are 0 topics")


# Returns a list of all users subscribing to a topic
def commandGetTopicUsersList(socket, topicName):
	usernames = []
	topicLabel = topicNameToLabel(topicName)

	# TODO: This algorithm is very unoptimized

	if topicLabel in g:
		sockets = [x for x in g[topicLabel]]
		sockets.remove('topicRootNode')

		
		for x in sockets:
			neighbors = list(nx.common_neighbors(g, userRootNode, x))
			if not neighbors is None:
				# There should only be one common neighbor and it should be the username
				usernames.append(userLabelToName(neighbors[0])

	listResponse(socket, usernames, 'This topic has 0 subscribers')

	


# Returns a list of all topics the user is subscribing to
def commandGetTopics(socket, *_):
	topicLabels = sorted(nx.common_neighbors(g, socket, topicRootNode))
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
def commandSubscripeToTopic(socket, topicName):
	topicLabel = topicNameToLabel(topicName)

	# Add edge between socket and topic
	g.add_edge(socket, topicLabel)

	# Add edge between topic and topicRootNode
	g.add_edge(topicLabel, topicRootNode)

	# TODO: Update RabbitMQ bindings


# Called to unsubscribe to a topic
@returnOnEmpty
def commandUnsubscripeToTopic(socket, topicName):
	topicLabel = topicNameToLabel(topicName)

	# Remove edge between socket and topic
	if topicLabel in g and topicLabel in g[socket]:
		g.remove_edge(socket, topicLabel)

		# Topic node is always connected to topicRootNode so degree>=1 always 
		if(g.degree(topicLabel) < 2):
			# Remove topic if no sockets subscribe to it
			g.remove_node(topicLabel)

	else:
		socket.write_message('You don\'t subscribe to that topic')
	
	# TODO: Update RabbitMQ bindings

	

@returnOnEmpty
def commandPrivateMessage(socket, message):
	messageParts = message.partition(" ")
	print "User: " + messageParts[0]
	print "Message: " + messageParts[2]

@returnOnEmpty
def commandTopicMessage(socket, message):
	messageParts = message.partition(" ")
	print "Topic: " + messageParts[0]
	print "Message: " + messageParts[2]



# A dictionary listing avaiable commands. Used to process input and generate help message
commands = {
	"/h": 	{'function': commandHelp, 				'helpString': 'get info on commands'},
	"/n": 	{'function': commandName, 				'helpString': 'get name or set new name'},
	"/t": 	{'function': commandGetTopics, 			'helpString': 'list the topics you subscribe to'},
	"/ts": 	{'function': commandSubscripeToTopic, 	'helpString': 'subscribe to topic: /ts <topic>'},
	"/tu": 	{'function': commandUnsubscripeToTopic, 'helpString': 'unsubscribe to topic: /tu <topic>'},
	"/lu": 	{'function': commandGetUsersList, 		'helpString': 'list users'},
	"/lt": 	{'function': commandGetTopicsList, 		'helpString': 'list topics'},
	"/lut": {'function': commandGetTopicUsersList, 	'helpString': 'list users in a specific topic: /lut <topic>'},
	"/pm": 	{'function': commandPrivateMessage,		'helpString': 'send private message: /pm <user> message'},
	"/tm": 	{'function': commandPrivateMessage,		'helpString': 'send message to topic: /tm <topic> message'}
}




# TODO: Nodes must be searchable by user name, for message routing
def addConnection(socket):
	socket.name = ''
	g.add_node(socket)
	commandHelp(socket)

def removeConnection(socket):
	# Remove username node
	try:
		userLabel = list(nx.common_neighbors(g, socket, userRootNode))
		for x in userLabel:
			g.remove_node(x)
	except nx.NetworkXError:
		pass
	
	# Remove socket node
	g.remove_node(socket)


def processMessage(socket,message):
	print "MESSAGE: %s" % message
	# Remove trailing whitespace
	message = message.rstrip();

	# Partition message to get command
	messageParts = message.partition(" ")

	# The command is the first element
	cmd = messageParts[0]

	if cmd in commands:
		# If the command is valid call the appropriate callback
		commands[cmd]['function'](socket, messageParts[2])
	else:
		routeMessage(socket,message)
		
def routeMessage(socket, message):
	if socket.name != '':
		# TODO: Proper routing. This simply sends the message to all other users
		for x in g[userRootNode]:
			if x != socket:
				x.write_message("%s: %s" % (socket.name, message))
	else:
		socket.write_message("You must set a username before you can send messages")


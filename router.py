import networkx as nx

userRootNode = 'userRootNode'
topicRootNode = 'topicRootNode'

# g stores connections between users and topics with
# one node for each user and one node for each topic.
# Users are accessed by getting neighbors of the userRootNode
# Topics are accessed by getting neighbors of the topicRootNode
g = nx.Graph()
g.add_node(userRootNode)
g.add_node(topicRootNode)




# Generates a message listing available commands and sends it to the user
def commandHelp(socket, *_):
	iteratorList = zip(commands.iterkeys(),commands.itervalues())
	helpList = ["%-10s %s" % (x[0],x[1][1]) for x in iteratorList]
	helpList.sort()
	socket.write_message("\n".join(helpList))

def commandName(socket, newName):
	if(newName == ''):
		try:
			socket.write_message('Your username: ' + socket.name)
		except:
			socket.write_message('You haven\'t set have a username yet')
	else:
		socket.name = newName
		socket.write_message('Your new username: ' + socket.name)


def commandGetUsersList(socket, *_):
	listResponse(socket, g.neighbors(userRootNode), "There are 0 users")


def	commandGetTopicsList(socket, *_):
	listResponse(socket, g.neighbors(topicRootNode), "There are 0 topics")


def commandGetTopicUsersList(socket, topic):
	try:
		nodeList = g.neighbors(topic).remove(topicRootNode)
	except nx.NetworkXError:
		nodeList = []

	listResponse(socket, nodeList, "There are 0 subscribers to this topic")


def commandGetTopics(socket, *_):
	nodeList = g.neighbors(socket).remove(userRootNode)
	listResponse(socket, nodeList, "You subscribe to 0 topics")


def listResponse(socket, nodeList, emptyResponse):
	response = emptyResponse
	if(len(nodeList) > 0):
		response = ["%s" % x.name for x in nodeList]
		response.sort()
		response = "\n".join(response)

		if response == '':
			response = emptyResponse

	socket.write_message(response)


def commandSubscripeToTopic(socket, topic):
	# Add edge between socket and topic
	# Update RabbitMQ bindings
	print 'commandSubscripeToTopic'

def commandUnsubscripeToTopic(socket, topic):
	# Remove edge between socket and topic
	# Update RabbitMQ bindings
	# If topic node has degree 0, remove it
	print 'commandUnsubscripeToTopic'


commands = {
	"/h": [commandHelp, 'get info on commands'],
	"/n": [commandName, 'get name or set new name'],
	"/t": [commandGetTopics, 'list the topics you subscribe to'],
	"/ts": [commandSubscripeToTopic, 'subscribe to topic: /ts <topic> '],
	"/tu": [commandUnsubscripeToTopic, 'unsubscribe to topic: /tu <topic> '],
	"/lu": [commandGetUsersList, 'list users'],
	"/lt": [commandGetTopicsList, 'list topics'],
	"/lut": [commandGetTopicUsersList, 'list users in a specific topic: /lut <topic>']
}





def addConnection(socket):
	socket.name = ''
	g.add_edge(userRootNode, socket)
	commandHelp(socket)

def removeConnection(socket):
	g.remove_node(socket)

def numberOfConnections():
	return g.degree(userRootNode)

def processMessage(socket,message):
	print "MESSAGE: %s" % message
	# Remove trailing whitespace
	message = message.rstrip();

	# Partition message to get command
	parts = message.partition(" ")

	# The command is the first element
	cmd = parts[0]

	if cmd in commands:
		# If the command is valid call the appropriate callback
		commands[cmd][0](socket,parts[2])
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


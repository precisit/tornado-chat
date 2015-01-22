
import tornado.websocket

class WebSocketHandler(tornado.websocket.WebSocketHandler):
	# Override standard functions open, on_message etc
	def open(self):
		self.write_message('Welcome')
		router.addConnection(self)
		print "WebSocket opened."

	def on_message(self, message):
		# TODO: Pass RabbitMQ channel so router can send messages to RabbitMQ
		router.processWebSocketMessage(self, message)

	def on_close(self):
		router.removeConnection(self)
		print "WebSocket closed."

	def check_origin(self, origin): # Very important. Cross-origin won't work otherwise
		print "server.check_origin(): Origin: " + origin
		return True


a = WebSocketHandler

# a.routing_key = 'test_routing_key'

print a.routing_key

# import networkx as nx
# g = nx.Graph()

# # a = ['ab','ac']
# # b = [x.lstrip('a') for x in a]

# # print a
# # print b

# userRootNode = 'userRootNode'
# g.add_node(userRootNode)

# g.add_edge(userRootNode, 'username1')
# g.add_edge(userRootNode, 'username2')
# g.add_edge(userRootNode, 'username3')


# g.add_edge('username1', 'socket1')
# g.add_edge('username2', 'socket2')
# g.add_edge('username3', 'socket3')


# g.add_edge('socket1', 'topic1')
# g.add_edge('socket2', 'topic1')

# g.add_edge('topic1','topicRootNode')


# # print [g[x] for x in g[userRootNode]]
# sockets = [x for x in g['topic1']]
# sockets.remove('topicRootNode')

# usernames = []
# for x in sockets:
# 	username = list(nx.common_neighbors(g, userRootNode, x))
# 	if not username is None:
# 		usernames.append(username[0])


# print usernames

# print [x for x in nx.common_neighbors(g, userRootNode, 'socket1')]

# print g[userRootNode].keys()

# print 'socket1' in g
# print userRootNode in g
# print 'lolg' in g
# print 'username1' in g

# print 'username1' in g[userRootNode]

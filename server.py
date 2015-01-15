import tornado.ioloop
import tornado.web
import tornado.websocket

# List for storing connections
sockets = []

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("message from server")

class EchoWebSocket(tornado.websocket.WebSocketHandler):
	# Override standard functions open, on_message etc
    def open(self):
        sockets.append(self)
        print "WebSocket opened. Connections: %d" % len(sockets)

    def on_message(self, message):
		for socket in sockets:
			if socket != self:
				socket.write_message(message)

    def on_close(self):
        sockets.remove(self)
        print "WebSocket closed. Connections: %d" % len(sockets)

    def check_origin(self, origin): # Very important. Cross-origin won't work otherwise
    	return True
		

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/websocket", EchoWebSocket),
])

if __name__ == "__main__":
	print "Starting server"
	application.listen(8080)
	tornado.ioloop.IOLoop.instance().start()

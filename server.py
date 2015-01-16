import tornado.ioloop
import tornado.web
import tornado.websocket
import uuid

# Internal dependencies
import router

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("message from server")

class EchoWebSocket(tornado.websocket.WebSocketHandler):
	# Override standard functions open, on_message etc
    def open(self):
    	self.write_message('Welcome')
    	router.addConnection(self)
        print "WebSocket opened. Connections: %d" % router.numberOfConnections()

    def on_message(self, message):
    	router.processMessage(self, message)

    def on_close(self):
    	router.removeConnection(self)
        print "WebSocket closed. Connections: %d" % router.numberOfConnections()

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

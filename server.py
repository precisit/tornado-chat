import tornado.ioloop
import tornado.web
import tornado.websocket
import sys

# Internal dependencies
import router
from pikaclient import PikaClient


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("message from server")


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
		

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/websocket", WebSocketHandler),
])

def main():
	print "Starting server"

	ioloop = tornado.ioloop.IOLoop.instance()

	# application.pikaClient = PikaClient(ioloop)
	# application.pikaClient.connect()

	pikaClient = PikaClient(ioloop)
	pikaClient.connect()

	router.pikaClient = pikaClient

	# Set port if port specified by user
	if(len(sys.argv) > 1):
		port = int(sys.argv[1])
	else:
		port = 8080

	print "listening on port %d" % port
	application.listen(port)
	ioloop.start()

if __name__ == "__main__":
	main()
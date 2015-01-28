import tornado.ioloop
import tornado.web
import tornado.websocket
import sys
import uuid
import json

# Internal dependencies
import router
from pikaclient import PikaClient



if(len(sys.argv) > 1):
	port = int(sys.argv[1])
else:
	port = 8080

# TODO: Make sure tickets expire after some time and are deleted after that time
wsTicketSet = set()

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("message from server")
		print "MainHandler: GET received"

	def post(self, *args, **kwargs):
		ticket = self.request.headers.get('Ticket') # The ticket is currently unused

		# Generate new ticket for connecting to websocket
		wsTicket = uuid.uuid4().hex
		wsTicketSet.add(wsTicket)

		response = {
			'WebSocketTicket': newWsTicket,
			'WebSocketPort': port
		}
		self.write(json.dumps(response))



class WebSocketHandler(tornado.websocket.WebSocketHandler):
	# Override standard functions open, on_message etc
	def open(self, wsTicket):
		if wsTicket in wsTicketSet:
			wsTicketSet.remove(wsTicket)
			self.write_message('Welcome')
			router.addConnection(self)
			print "WebSocket opened."
		else:
			print "Websocket connection with invalid ticket refused"
			self.write_message('Invalid ticket, connection refused')
			self.close(reason='Invalid ticket')

	def on_message(self, message):
		router.processWebSocketMessage(self, message)

	def on_close(self):
		router.removeConnection(self)
		print "WebSocket closed."

	def check_origin(self, origin): # Very important. Cross-origin won't work otherwise
		print "server.check_origin(): Origin: " + origin
		return True
		

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/websocket/(.*)", WebSocketHandler),
], autoreload=True)

def main():
	print "Starting server"

	ioloop = tornado.ioloop.IOLoop.instance()

	pikaClient = PikaClient(ioloop)
	pikaClient.connect()

	router.pikaClient = pikaClient

	# Set port if port specified by user
	

	print "Server listening on port %d" % port
	application.listen(port)
	ioloop.start()

if __name__ == "__main__":
	main()
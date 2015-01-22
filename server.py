import tornado.ioloop
import tornado.web
import tornado.websocket
import pika

# from pika.adapters.tornado_connection import TornadoConnection

# Internal dependencies
import router

# Configuration parameters
rabbitmq_exchange_name = 'tornado-chat'


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
		router.processMessage(self, message)

	def on_close(self):
		router.removeConnection(self)
		print "WebSocket closed."

	def check_origin(self, origin): # Very important. Cross-origin won't work otherwise
		print "server.check_origin(): Origin: " + origin
		return True


class PikaClient(object):

	def __init__(self, io_loop):
		print 'PikaClient: __init__'
		self.io_loop = io_loop

		self.connected = False
		self.connecting = False
		self.connection = None
		self.channel = None

		self.event_listeners = set([])

	def connect(self):
		if self.connecting:
			print 'PikaClient: Already connecting to RabbitMQ'
			return

		print 'PikaClient: Connecting to RabbitMQ'
		self.connecting = True

		# cred = pika.PlainCredentials('guest', 'guest')
		param = pika.ConnectionParameters(
			host='localhost',
			# port=5672,
			# virtual_host='/',
			# credentials=cred
		)

		self.connection = pika.adapters.tornado_connection.TornadoConnection(
			param,
			on_open_callback=self.on_connected
		)
		self.connection.add_on_close_callback(self.on_closed)

	def on_connected(self, connection):
		print 'PikaClient: connected to RabbitMQ'
		self.connected = True
		self.connection = connection
		self.connection.channel(self.on_channel_open)

	def on_channel_open(self, channel):
		print 'PikaClient: Channel open, Declaring exchange'
		self.channel = channel
		# declare exchanges, which in turn, declare
		# queues, and bind exchange to queues

		# Declare exchange
		channel.exchange_declare(
			exchange = rabbitmq_exchange_name,
			type = 'topic'
		)

		# Declare queue
		print channel.queue_declare(self.on_queue_declare_ok, exclusive=True, auto_delete=True)
		

	def on_queue_declare_ok(self, queue):
		queue_name = queue.method.queue

		# Bind queue to exchange
		self.channel.queue_bind(
			self.on_bind_ok,
			exchange = rabbitmq_exchange_name,
			queue = queue_name,
			routing_key = 'hello'
		)

		# Declare callback for messages
		self.channel.basic_consume(
			self.on_message,
			queue = queue_name,
			no_ack = True
		)

		
	def on_bind_ok(self, frame):
		# Send test message
		self.channel.basic_publish(
			exchange = rabbitmq_exchange_name,
			routing_key = 'hello',
			body = 'test message sent through RabbitMQ'
		)
 
	def on_closed(self, connection):
		print 'PikaClient: rabbit connection closed'
		self.io_loop.stop()
 
	def on_message(self, channel, method, header, body):
		# print 'PikaClient: message received: %s' % body
		print 'PikaClient: message received:'
		print 'channel:'
		print channel
		print 'method:'
		print method
		print 'header:'
		print header
		print 'body:'
		print body
		# router.process_rabbitmq_message(body)
		print 'routing_key:'
		print method.routing_key




		

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

	application.listen(8080)
	ioloop.start()

if __name__ == "__main__":
	main()
import pika
import router

from pika.adapters.tornado_connection import TornadoConnection

# Configuration parameters
rabbitmq_exchange = 'tornado-chat-2'
server_routing_key = 'server_routing_key'

class PikaClient(object):

	def __init__(self, io_loop):
		print 'PikaClient: __init__'
		self.io_loop = io_loop

		self.connected = False
		self.connecting = False
		self.connection = None
		self.channel = None
		self.client_queue = None
		self.server_queue = None

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

		self.connection = TornadoConnection(
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

		# Declare exchange
		channel.exchange_declare(
			exchange = rabbitmq_exchange,
			type = 'direct'
		)

		# Declare client queue
		channel.queue_declare(self.on_client_queue_declare_ok, queue='client_queue', exclusive=True, auto_delete=True)

		# Declare server queue
		channel.queue_declare(self.on_server_queue_declare_ok, queue='server_queue', exclusive=True, auto_delete=True)
		

	def on_client_queue_declare_ok(self, queue):
		self.client_queue = queue.method.queue

		# Declare callback for messages
		self.channel.basic_consume(
			self.on_client_message,
			queue = self.client_queue,
			no_ack = True
		)

	def on_server_queue_declare_ok(self, queue):
		self.server_queue = queue.method.queue

		
		# Declare callback for messages
		self.channel.basic_consume(
			self.on_server_message,
			queue = self.server_queue,
			no_ack = True
		)

		# Bind queue
		self.channel.queue_bind(
			self.on_bind_ok,
			exchange = rabbitmq_exchange,
			queue = self.server_queue,
			routing_key = server_routing_key
		)


	def send_user_message(self, routing_key, message):
		self.channel.basic_publish(
			exchange = rabbitmq_exchange,
			routing_key = routing_key,
			body = message
		)

	def send_server_message(self, message):
		self.channel.basic_publish(
			exchange = rabbitmq_exchange,
			routing_key = server_routing_key,
			body = message
		)
 
	def on_closed(self, connection):
		print 'PikaClient: rabbit connection closed'
		self.io_loop.stop()
 
	def on_client_message(self, channel, method, header, body):
		router.rabbitProcessClientMessage(method.routing_key, body)

	def on_server_message(self, channel, method, header, body):
		router.rabbitProcessServerMessage(method.routing_key, body)

	def bind_client_queue(self, routing_key):
		self.channel.queue_bind(
			self.on_bind_ok,
			exchange = rabbitmq_exchange,
			queue = self.client_queue,
			routing_key = routing_key
		)

	def on_bind_ok(self, frame):
		pass

	def timed_bind_server_queue(self, seconds, routing_key):
		self.channel.queue_bind(
			self.on_bind_ok,
			exchange = rabbitmq_exchange,
			queue = self.server_queue,
			routing_key = routing_key
		)
		self.io_loop.call_later(seconds, self.unbind, routing_key)

	def unbind_client_queue(self, routing_key):
		self.channel.queue_unbind(
			self.on_bind_ok,
			exchange = rabbitmq_exchange,
			queue = self.client_queue,
			routing_key = routing_key
		)

	def on_unbind_ok(self, frame):
		pass
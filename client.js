var WebSocket = require('ws');
var promptModule = require('cli-input');

var inputParser = require('./inputParser');
var connector = require('./connector');

var ticket = 'This-is-a-test-ticket';

var port = 8080;
if (process.argv.length > 2) {
	port = process.argv[2];
}


var connection;
function onReceiveConnection(newConnection) {
	connection = newConnection;

	// Overriding functions for websockethandler
	connection.onopen = function open() {
		// Enable sending stuff to the server
		prompt.run()
	};

	connection.on('close', function close() {
		console.log('Disconnected from server');
		exit();
	});

	connection.on('message', function message(data, flags) {
		console.log(data);
	});
}
connector.connect(port, ticket, onReceiveConnection);


// Initialize prompt
var prompt = promptModule({
	input: process.stdin,
	output: process.stderr,
	infinite: true,
	prompt: '',
	name: ''
});

prompt.on('value', function(line) {
	if (line[0] === '/quit') {
		exit();
	}
	else {
		connection.send(inputParser.format(line), {mask: true});
	}
});


// For exiting
function exit() {
	connection.close(); // Close websocket connection
	console.log('Goodbye');
	process.exit();
}
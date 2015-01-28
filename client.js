var WebSocket = require('ws');
var promptModule = require('cli-input');
var inputParser = require('./inputParser');
var http = require('http');

var port = 8080;

var connection;

if (process.argv.length > 2) {
	port = process.argv[2];
}

// Connect to server over http
var options = {
	method: 'POST',
	port: port,
	headers: {'Ticket': 'This-is-a-test-ticket'}
};
var request = http.request(options, function(response) {
	response.setEncoding('utf8');

	response.on('data', function (chunk) {
		data = JSON.parse(chunk);
		setup_websocket_connection(data['WebSocketPort'], data['WebSocketTicket']);
	});
});
request.write('hello world\n');
request.end();



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
		connection.send(inputParser.input_to_json_string(line), {mask: true});
	}
});

function setup_websocket_connection(webSocketPort, webSocketTicket) {
	console.log("Attempting to connect websocket");

	connection = new WebSocket('ws://0.0.0.0:' + webSocketPort + '/websocket/' + webSocketTicket);

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


// For exiting
function exit() {
	connection.close(); // Close websocket connection
	console.log('Goodbye');
	process.exit();
}
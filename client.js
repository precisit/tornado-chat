var WebSocket = require('ws');
var promptModule = require('cli-input');

var port = 8080;

if (process.argv.length > 2) {
	port = process.argv[2];
}

// Open websocket TODO: Error handling
var connection = new WebSocket('ws://0.0.0.0:' + port + '/websocket');

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
		var message = {};
		console.log(line);
		if (line[0][0] === '/') {
			message.command =  String(line.splice(0,1));
			message.argument = String(line.splice(0,1));
		}
		message.payload = line.join(' ');

		connection.send(JSON.stringify(message), {mask: true});
	}
});

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


// For exiting
function exit() {
	connection.close(); // Close websocket connection
	console.log('Goodbye');
	process.exit();
}
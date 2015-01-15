var WebSocket = require('ws');
var readline = require('readline');
var username;

// Open websocket TODO: Error handling
var connection = new WebSocket('ws://0.0.0.0:8080/websocket');

// Initialize prompt
var rl = readline.createInterface(process.stdin, process.stdout);
rl.on('SIGINT', exit);

// Overriding functions for websockethandler
connection.onopen = function open() {
	console.log('Connected to server');
  
  	// Ask for a username
	rl.question('Enter a username: ', function (input) {
		username = input;

		// Enable sending stuff to the server
		rl.on('line', inputHandler);
	});
};

connection.on('close', function close() {
  console.log('Disconnected from server');
  exit();
});

connection.on('message', function message(data, flags) {
  console.log(data);
});

// For handling input from user
function inputHandler(line) {
	if (line === 'quit') {
		exit();
	}
	else {
		connection.send(username + ': ' + line, {mask: true});
	}
}

// For exiting
function exit() {
	connection.close(); // Close websocket connection
	console.log('Goodbye');
	process.exit();
}
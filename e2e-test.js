var WebSocket = require('ws');


//<configuration parameters>
var numberOfSockets = 3; //The number of sockets to connect to the server
var j = 0; // Initial delay in time units, counter for delay
var t = 10; // Milliseconds per time unit
//</configuration parameters>


var sockets = [];
var connected = 0;

// Setup connections
for (var i = 0; i < numberOfSockets; i++) {
	sockets[i] = new WebSocket('ws://0.0.0.0:8080/websocket');

	sockets[i].onopen = function onopen() {
		// Increment the number of connected sockets
		connected++;

		// If all sockets connected
		if(connected == numberOfSockets) {
			// Commence testing shortly
			setTimeout(beginTest, 100);
		}
	};
};

var latestData;

function beginTest() {
	for (var i = 0; i < numberOfSockets; i++) {

		// TODO: Proper onmessage so each socket can store it's latest data separately
		sockets[i].onmessage = function message(data, flags) {
			// pr('INCOMING: ' + data['data']);
			latestData = data['data'];
		}

		// Set names
		sockets[i].send('/n ' + i);
	}

	// Register different tests. See below for implementation of function registerTest.
	// Essentially timeouts are set to send commands and check responses in a specific order.

	var topic = 'someTopic';
	registerTest(
		'join topic, get proper subscription list',
		[0,					0],
		['/ts ' + topic, 	'/t'],
		topic
	);


	registerTest(
		'get proper topic list for other socket',
		[1],
		['/lt'],
		topic
	);


	registerTest(
		'get proper subscriber list for topic',
		[0],
		['/ltu ' + topic],
		'0'
	);


	registerTest(
		'leave topic, get proper subscription list',
		[0,					0],
		['/tu ' + topic,	'/t'],
		'You subscribe to 0 topics'
	);


	registerTest(
		'get proper topic list for other socket',
		[1],
		['/lt'],
		'There are 0 topics'
	);


	j++;
	setTimeout( function () {process.exit()}, j*t);
}





// testString: String explaining the test
// socketIndices: a list of socket indices to which the commands should be sent
// commands: a list of commands to send to the sockets indicated by socketIndices
// expectedData: the expected return from the server after the last command has been sent
function registerTest(testString, socketIndices, commands, expectedData) {
	// Set timeouts for sending commands
	for (var i = 0; i < commands.length; i++) {
		j++;
		setTimeout(getSendFunction(socketIndices[i], commands[i]), j*t);
	}

	// Set timeout for checking result
	j++;
	setTimeout( function () {
		passed = (latestData == expectedData);

		// Print information on whether test passed or failed
		pr((passed ? 'PASSED' : 'FAILED') + '\t' + testString);

		// If the test didn't pass
		if (!passed) {
			// Print info on what was expected and what was received
			pr('\t expected: ' + expectedData);
			pr('\t received: ' + latestData);
		}
	}, j*t);
}

// Didn't figure out how to do this properly with an anonymous function so here's a regular function instead
function getSendFunction(socketIndex, command) {
	return function () {
		sockets[socketIndex].send(command);
	};
}


// Function for printing
function pr(s) {
	console.log(s);
}
var WebSocket = require('ws');


var numberOfSockets = 3; 
var sockets = [];
var connected = 0;

// Create sockets
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
	pr('beginTest called');
	for (var i = 0; i < numberOfSockets; i++) {
		sockets[i].onmessage = function message(data, flags) {
			// pr('INCOMING: ' + data['data']);
			latestData = data['data'];
		}

		sockets[i].send('/n ' + i);
	}


	var topic = 'cars';
	registerTest(
		'join topic, get proper topic list',
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
		'get proper user list for topic',
		[0],
		['/ltu ' + topic],
		'0'
	);


	registerTest(
		'leave topic, get proper topic list',
		[0,					0],
		['/tu ' + topic,		'/t'],
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

var j = 0; // Initial delay in time units, counter for delay
var t = 10; // Milliseconds per time unit
function registerTest(testName, socketIndices, commands, expectedData) {
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
		pr((passed ? 'PASSED' : 'FAILED') + '\t' + testName);

		// If the test didn't pass
		if (!passed) {
			// Print info on what was expected and what was received
			pr('\t expected: ' + expectedData);
			pr('\t received: ' + latestData);
		}
	}, j*t);
}

function getSendFunction(socketIndex, command) {
	return function () {
		sockets[socketIndex].send(command);
	};
}

function pr(s) {
	console.log(s);
}
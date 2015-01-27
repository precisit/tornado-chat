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
			setTimeout(beginTest, 500);
		}
	};
};

var latestData = [];

function onmessageFunction(i) {
	return function (data, flags) {
		latestData[i] = data['data'];
	};
}

function beginTest() {
	for (var i = 0; i < numberOfSockets; i++) {
		// Set callback
		sockets[i].onmessage = onmessageFunction(i);

		// Set names
		sockets[i].send('/n ' + i);
	}

	// Register different tests. See below for implementation of function registerTest.
	// Essentially timeouts are set to send commands and check responses in a specific order.

	var topic = 'someTopic';
	var message = 'someMessage';
	var name = 'someName';


	registerTest(
		'unable to send message without setting username',
		[0],
		[message],
		0,
		'fffdfggrrr5b'
	)


	// for (var i = 0; i < numberOfSockets; i++) {
	// 	// Set names
	// 	sockets[i].send('/n ' + i);
	// }
	

	registerTest(
		'join topic, get proper subscription list',
		[0,				0],
		['/ts '+topic, 	'/t'],
		0,
		topic
	);


	registerTest(
		'get proper topic list for other socket',
		[1],
		['/lt'],
		0,
		topic
	);


	registerTest(
		'get proper subscriber list for topic',
		[0],
		['/ltu '+topic],
		0,
		'0'
	);


	registerTest(
		'leave topic, get proper subscription list',
		[0,				0],
		['/tu '+topic,	'/t'],
		0,
		'You subscribe to 0 topics'
	);


	registerTest(
		'get proper topic list for other socket',
		[1],
		['/lt'],
		1,
		'There are 0 topics'
	);


	registerTest(
		'send private message from one user to another', 
		[0],
		['/mu 1 '+message],
		1,
		'0: '+message
	)


	registerTest(
		'send topic message',
		[1,				2,				0],
		['/ts '+topic, 	'/ts '+topic, 	'/mt '+topic+' '+message],
		1,
		'0: '+message
	)


	registerTest(
		'send topic message',
		[1,				2,				0],
		['/ts '+topic, 	'/ts '+topic, 	'/mt '+topic+' '+message],
		2,
		'0: '+message
	)


	registerTest(
		'unable to change name to existing name',
		[0],
		['/n 1'],
		0,
		"Username '1' is not available"
	)


	registerTest(
		'able to change name',
		[0],
		['/n '+name],
		0,
		'Your new username: '+name
	)


	registerTest(
		'able to change name back again',
		[0],
		['/n 0'],
		0,
		'Your new username: 0'
	)


	registerTest(
		'unable to send message without setting address',
		[0],
		[message],
		0,
		'No address is set. See help (/h)'
	)


	registerTest(
		'able to send private message after setting address',
		[0,			0],
		['/au 1',	message],
		1,
		'0: '+message
	)


	registerTest(
		'able to send topic message after setting address',
		[0,				1,				0],
		['/at '+topic,	'/ts '+topic,	message],
		1,
		'0: '+message
	)


	j++;
	setTimeout( function () {process.exit()}, j*t);
}





// testString: String explaining the test
// socketIndices: a list of socket indices to which the commands should be sent
// commands: a list of commands to send to the sockets indicated by socketIndices
// socketIndex: index of socket for which to compare latest data with expected data
// expectedData: the expected return from the server after the last command has been sent
function registerTest(testString, socketIndices, commands, socketIndex, expectedData) {
	// Set timeouts for sending commands
	for (var i = 0; i < commands.length; i++) {
		j++;
		setTimeout(sendFunction(socketIndices[i], commands[i]), j*t);
	}

	// Set timeout for checking result
	j++;
	setTimeout( function () {
		received = latestData[socketIndex]
		passed = (received == expectedData);

		// Print information on whether test passed or failed
		pr((passed ? '[X] PASSED' : '[ ] FAILED') + '\t' + testString);

		// If the test didn't pass
		if (!passed) {
			// Print info on what was expected and what was received
			pr('\t expected: \'' + expectedData + '\'');
			pr('\t received: \'' + received + '\'');
		}
	}, j*t);
}

// Didn't figure out how to do this properly with an anonymous function so here's a regular function instead
function sendFunction(socketIndex, command) {
	return function () {
		sockets[socketIndex].send(command);
	};
}


// Function for printing
function pr(s) {
	console.log(s);
}
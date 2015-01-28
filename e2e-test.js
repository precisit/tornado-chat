var WebSocket = require('ws');
var inputParser = require('./inputParser');
var connector = require('./connector');

var port = 8080;
if (process.argv.length > 2) {
	port = process.argv[2];
}


//<configuration parameters>
var numberOfSockets = 3; //The number of sockets to connect to the server. Should be at least 2.
var j = 0; // Initial delay in time units, counter for delay
var t = 10; // Milliseconds per time unit
//</configuration parameters>


var sockets = []; // Array of sockets
var latestData = []; // Array of the latest data received by each socket
var connected = 0; // Counter for number of successfully connected sockets

// Setup connections
for (var i = 0; i < numberOfSockets; i++) {
	connector.connect(port, '', onReceiveConnection(i));
}

function onReceiveConnection(i) {
	return function(connection) {
		sockets[i] = connection;

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
}






function onMessageFunction(i) {
	return function (data, flags) {
		latestData[i] = data['data'];
	};
}

function beginTest() {
	for (var i = 0; i < numberOfSockets; i++) {
		// Set callback
		sockets[i].onmessage = onMessageFunction(i);
	}

	// Register different tests. See below for implementation of function registerTest.
	// Essentially timeouts are set to send commands and check responses in a specific order.

	var topic = 'someTopic';
	var message = 'someMessage';
	var name = 'someName';


	registerTest(
		'unable to send message without setting username',
		[0,				0],
		['/at '+topic,	message],
		0,
		'You must set a username before you can send messages'
	)

	var nameCommandList = [];
	var socketIndexList = [];
	for (var i = 0; i < numberOfSockets; i++) {
		socketIndexList[i] = i;
		nameCommandList[i] = ('/n '+i);
	}

	registerTest(
		'able to set username',
		socketIndexList,
		nameCommandList,
		0,
		'Your new username: 0'
	)
	

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
		1,
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
		[1],
		[message],
		1,
		'No address is set. See help (/h)'
	)


	registerTest(
		'get user name',
		[1],
		['/n'],
		1,
		'Your username: 1'
	)


	registerTest(
		'subscribe to a topic again, get proper list of subscriptions',
		[1,				1],
		['/ts '+topic,	'/t'],
		1,
		topic
	)


	registerTest(
		'able to send topic message after setting address',
		[0,				1,				0,			0,			0,			0],
		['/at '+topic,	'/ts '+topic,	message,	message,	message,	message],
		1,
		'0: '+message
	)


	registerTest(
		'able to send private message after setting address',
		[0,			0],
		['/au 1',	message],
		1,
		'0: '+message
	)

	// registerTest(
	// 	'able to send topic message after setting address',
	// 	[0,				1,				0],
	// 	['/at '+topic,	'/ts '+topic,	message],
	// 	1,
	// 	'0: '+message
	// )


	j++;
	setTimeout( function () {process.exit()}, j*t);
}



var testsTotal = 0;
var testsPassed = 0;
var testsFailed = 0;

// testString: String explaining the test
// socketIndices: a list of socket indices to which the commands should be sent
// commands: a list of commands to send to the sockets indicated by socketIndices
// socketIndex: index of socket for which to compare latest data with expected data
// expectedData: the expected return from the server after the last command has been sent
function registerTest(testString, socketIndices, commands, socketIndex, expectedData) {
	testsTotal++;
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
		if (passed) {
			testsPassed++;
		} else {
			testsFailed++;
		}

		// Print information on whether test passed or failed
		pr((passed ? '[X] PASSED' : '[ ] FAILED') + '\t' + testString);

		// If the test didn't pass
		if (!passed) {
			// Print info on what was expected and what was received
			pr('\t expected: \'' + expectedData + '\'');
			pr('\t received: \'' + received + '\'');
		}

		// Clear latest data for next test
		for (var i = 0; i < numberOfSockets; i++) {
			latestData[i] = 'reset';
		}

		if (testsTotal == testsPassed + testsFailed) {
			pr('\nTESTS PASSED: ' + testsPassed + '/' + testsTotal + '\n');
		}
	}, j*t);
}

// Didn't figure out how to do this properly with an anonymous function so here's a regular function instead
function sendFunction(socketIndex, command) {
	return function () {
		sockets[socketIndex].send(inputParser.format(command.split(' ')));
	};
}


// Function for printing
function pr(s) {
	console.log(s);
}
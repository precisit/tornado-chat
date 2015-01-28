var http = require('http');
var WebSocket = require('ws');

function connect(port, ticket, callback) {
	// Connect to server over http
	var options = {
		method: 'POST',
		port: port,
		headers: {'Ticket': ticket}
	};
	var request = http.request(options, function(response) {
		response.setEncoding('utf8');

		response.on('data', function (chunk) {
			data = JSON.parse(chunk);
			webSocketPort = data['WebSocketPort'];
			webSocketTicket = data['WebSocketTicket'];
			connection = new WebSocket('ws://0.0.0.0:' + webSocketPort + '/websocket/' + webSocketTicket);
			callback(connection);
		});
	});
	request.end();
}

module.exports.connect = connect;
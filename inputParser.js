function format(line) {
	var message = {};

	if (line[0][0] === '/') {
		message.command =  String(line.splice(0,1));
		message.argument = String(line.splice(0,1));
	}
	message.payload = line.join(' ');

	return JSON.stringify(message);
}

module.exports.format = format;
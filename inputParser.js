function input_to_json_string(line) {
	var message = {};

	if (line[0][0] === '/') {
		message.command =  String(line.splice(0,1));
		message.argument = String(line.splice(0,1));
	}
	message.payload = line.join(' ');

	return JSON.stringify(message);
}

module.exports.input_to_json_string = input_to_json_string;
def split_args(arguments):
	import re

	temp_arguments_list = []

	number = 0
	number_of_arguments = len(arguments) - 1

	while number <= number_of_arguments:
		grouped_short_options = re.match('^-[a-zA-Z0-9][a-zA-Z0-9]', arguments[number])

		if bool(grouped_short_options) == True:

			for letter in arguments[number].replace('-', ''):
				temp_arguments_list += ["-" + letter]

		else:
			temp_arguments_list += [arguments[number]]

		number = number + 1

	return temp_arguments_list

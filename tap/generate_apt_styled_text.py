def generate_apt_styled_text(header, packages):
	returned_text = f"{header}\n"

	package_text_list = " "

	for i in packages:
		package_text_list += f" {i}"

	returned_text += package_text_list

	return returned_text

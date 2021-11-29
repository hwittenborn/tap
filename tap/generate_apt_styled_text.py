def generate_apt_styled_text(header, packages):
    from os import get_terminal_size
    
    terminal_width = get_terminal_size().columns

    if len(packages) == 0:
        return

    output_text = f"{header}\n "
    package_length = len(packages)
    current_line_length = 1

    for i in range(package_length):
        current_pkg = packages[i]
        output_text += f" {current_pkg}"
        current_line_length += (1 + len(current_pkg))
        
        if i + 1 == package_length:
            continue
        elif current_line_length + (1 + len(packages[i+1])) > terminal_width:
            output_text += "\n "
            current_line_length = 1

    print(output_text)

def message(type, message, **args):
    from functions.colors import colors # REMOVE AT PACKAGING

    value_return = False

    if args.get("value_return") == True:
        value_return = True

    if type == "info":
        message_string = f"{colors.bold_green}[##]{colors.bold_white} {message}{colors.white}"
    elif type == "warning":
        message_string = f"{colors.bold_yellow}[!!]{colors.bold_white} {message}{colors.white}"
    elif type == "warning2":
        message_string = f"  {colors.bold_yellow}[>]{colors.bold_white} {message}{colors.white}"
    elif type == "error":
        message_string = f"{colors.bold_red}[!!]{colors.bold_white} {message}{colors.white}"
    elif type == "error2":
        message_string = f"  {colors.bold_red}[>]{colors.bold_white} {message}{colors.white}"
    elif type == "question":
        message_string = f"{colors.bold_cyan}[??]{colors.bold_white} {message}{colors.white}"
    else:
        raise Exception("Invalid message type")

    if value_return == False:
        print(message_string)
    elif value_return == True:
        return message_string

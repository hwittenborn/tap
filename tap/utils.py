from tap.colors import colors
from tap.exceptions import UnknownPackage
from tap.message import message
from tap import cfg
from apt_pkg import TagFile, CURSTATE_INSTALLED


def _is_integer(arg):
    try:
        int(arg)
        return True
    except ValueError:
        return False


def is_installed(pkgname):
    installed = False

    try:
        if cfg.apt_cache[pkgname].current_state == CURSTATE_INSTALLED:
            installed = True
    except KeyError:
        installed = False

    if not installed:
        return False

    with TagFile("/var/lib/dpkg/status") as file:
        for section in file:
            if section["Package"] == pkgname:
                try:
                    section["MPR-Package"]
                    return "mpr"
                except KeyError:
                    return "apt"


def get_user_selection(question, options, **kwargs):
    msg2_function = kwargs["msg2_function"]
    multi_option = kwargs.get("multi_option", True)
    number_of_options = len(options)

    print()
    print(question.strip())

    # We'll start counting as 0, so subtract one from the recorded length for the number iterator.
    for number, option in enumerate(options):
        msg2_function(f"{option} [{number}]")

    if multi_option:
        msg = "Please select any combination of items."
    else:
        msg = "Please select an option."

    msg = message.question(
        f"{msg} [0-{number_of_options - 1}] ", newline=False, value_return=True
    )
    bad_response = True
    first_loop = True

    # Validate user's selection.
    while bad_response:
        if not first_loop:
            message.error("Invalid response.")
        response = input(msg)
        bad_response = False
        first_loop = False
        selected_options = []

        if response.split(",") == []:
            bad_response = True
            continue

        for i in response.split(","):
            if len(i) == 1:
                if (not _is_integer(i)) or (int(i) > number_of_options - 1):
                    bad_response = True
                    break

                selected_options += [options[int(i)]]
                continue

            elif len(i) != 3:
                bad_response = True
                break

            numbers = i.split("-")

            if len(numbers) != 2:
                bad_response = True
                break

            for i in numbers:
                if (not _is_integer(i)) or (int(i) > number_of_options - 1):
                    bad_response = True
                    break

            # The right side of the index selector appears to need to be one higher than the actual element to select said element (along with everything else that gets selected normally).
            num1 = int(numbers[0])
            num2 = int(numbers[1]) + 1
            selected_options += options[num1:num2]

            if (not multi_option) and (len(selected_options) != 1):
                bad_response = True
                continue

    if multi_option:
        return selected_options
    else:
        return selected_options[0]

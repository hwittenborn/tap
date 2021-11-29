comparison_operators = [">=", "<=", ">", "<", "="] 

class split_dependency_string:
    def __init__(self, string):
        operator = None

        for i in comparison_operators:
            if i in string:
                operator = i
                split_string = string.split(i)
                break

        if operator is None:
            self.pkgname = string
            self.operator = None
            self.pkgver = None

        else:
            self.pkgname = split_string[0]
            self.operator = operator
            self.pkgver = split_string[1]

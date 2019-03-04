from persistence import load, save


class Symbol(object):
    SYMTABLE_START = "Symbol table '.symtab'"
    SYMTABLE_HEADER = "Num:"

    def __set_fields(self, _address, _size, _type, _bind, _vis, _ndx, _name):
        self.address = int(_address, 16)
        self.size = int(_size, 16) if "0x" in _size else int(_size)
        self.type = _type
        self.bind = _bind
        self.vis = _vis
        self.ndx = _ndx
        self.name = _name

    def __init__(self, line):
        tokens = line.split()
        self.__set_fields(tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6],
                          tokens[7] if len(tokens) is 8 else "NONAME")

    def __str__(self):
        return hex(self.address) + ", type: " + self.type + ", scope: " + self.bind + ", name: " + self.name

    @staticmethod
    def diff(old_symbols, new_symbols):
        modified_or_new = set()
        for func in new_symbols:
            if func in old_symbols:
                for sym_name in new_symbols[func]:
                    if sym_name in old_symbols[func]:
                        if new_symbols[func][sym_name] != old_symbols[func][sym_name]:
                            modified_or_new.add(func)
                            break
                        else:  # Data is same
                            continue
                    else:  # sym is new
                        modified_or_new.add(func)
                        break

            else:  # ignore new functions
                continue
        return modified_or_new


class Function(Symbol):

    def __init__(self, line, checksum):
        Symbol.__init__(self, line)
        self.checksum = checksum
        self.calls = set()

    def call(self, func):
        self.calls.add(func)

    def __str__(self):
        return Symbol.__str__(self) + ", checksum: " + self.checksum

    @staticmethod
    def write(functions, filename):
        """Write functions to a file.

        Args:
            functions: A list of functions and their checksums
            filename: Name of file to store in

        Returns:
            None

        Raises:
            None
        """
        save(functions, filename)

    @staticmethod
    def read(filename):
        """Read functions from a file.

        Args:
            filename: Name of file which stored in

        Returns:
            Functions

        Raises:
            None
        """
        return load(filename)

    @staticmethod
    def diff(old_functions, new_functions):
        modified_or_new = set()
        skipped = set()
        for f in new_functions:
            if f in old_functions:
                # modified function
                if old_functions[f] != new_functions[f]:
                    modified_or_new.add(f)
                else:
                    skipped.add(f)
            else:  # new function
                modified_or_new.add(f)
        return modified_or_new, skipped

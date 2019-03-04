# import zlib
# from collections import defaultdict
from sys import stderr

from collections import defaultdict

import zlib

from ConstantPool import ConstantPool
from Section import Section
from Symbol import Symbol
from Graph import Graph
from hasher import checksum_ins_line
from runner import run_process


def get_all_functions(binary):
    """Get local and global functions in binary.

    Args:
        binary: ELF binary.

    Returns:
        List functions in the binary.

    Raises:
        None
    """
    functions = {}
    functions_by_addr = {}
    symtable_found = False
    for line in run_process(ConstantPool.READELF.format(binary)):
        if line.strip().startswith(Symbol.SYMTABLE_START):
            symtable_found = True
        elif line.strip().startswith(Symbol.SYMTABLE_HEADER):
            continue
        elif line.strip():
            symbol = Symbol(line.strip())
            if symbol.type == "FUNC":
                functions[symbol.name] = symbol
                functions_by_addr[symbol.address] = symbol

    if not symtable_found:
        print >> stderr, "{} not found in binary {}!".format(Symbol.SYMTABLE_START, binary)

    return functions, functions_by_addr


def get_callgraph(functions, binary):
    """Create a dictionary between caller -> callees*

    Args:
        functions: Set of functions
        binary: ELF binary

    Returns:
        Dictionary from callers to callees
        Functions and their checksums

    Raises:
        None
    """
    graph = Graph()
    new_functions = {}
    current_function_name = None
    for line in run_process(ConstantPool.OBJDUMP.format(binary)):
        line = line.rstrip()
        # a function start is detected
        match = ConstantPool.FUNC_ENTRY.match(line)
        if match:
            current_function_name = match.group(2)
            if current_function_name not in functions:
                continue
            new_functions[current_function_name] = 1
            continue
        # a function call is detected
        match = ConstantPool.FUNC_CALL.match(line)
        if match:
            if current_function_name in functions and match.group(3) in functions:
                graph.add_edge(current_function_name, match.group(3))
        match = ConstantPool.FUNC_CALL_2.match(line)
        if match:
            if current_function_name in functions and match.group(3) in functions:
                graph.add_edge(current_function_name, match.group(3))
        # update checksum using current line
        if current_function_name and current_function_name in functions:
            new_functions[current_function_name] = checksum_ins_line(line, new_functions[current_function_name])

    return graph, new_functions


def get_test_functions(all_functions):
    """Finds test functions, startsWith tc_ | utc_ | itc_.

    Args:
        all_functions: List of all functions.

    Returns:
        Test functions.

    Raises:
        None
    """
    test_funcs = []
    for name, adler32 in all_functions.iteritems():
        if ConstantPool.FUNC_TEST.match(name):
            test_funcs.append(name)
    return test_funcs


def get_leaf_test_functions(graph, test_functions):
    """Finds leaf test functions, they don't call any test function.

    Args:
        graph: Call graph
        test_functions: List of test functions.

    Returns:
        Leaf test functions.

    Raises:
        None
    """
    return [t for t in test_functions if ConstantPool.FUNC_TEST.match(t) and ("tc_main" not in t) and graph.is_leaf_test(t)]


def get_symbols_in_functions(functions, sym_functions_by_addr, symbols_by_address, binary):
    """Create a dictionary between caller -> callees*

    Args:
        functions: Set of functions
        binary: ELF binary

    Returns:
        Dictionary from callers to callees
        Functions and their checksums

    Raises:
        None
    """
    new_functions = {}
    current_function_name = None
    for line in run_process(ConstantPool.OBJDUMP.format(binary)):
        line = line.rstrip()
        # a function start is detected
        match = ConstantPool.FUNC_ENTRY.match(line)
        if match:
            current_function_name = match.group(2)
            if current_function_name not in functions:
                continue
            new_functions[current_function_name] = []
            continue
        if current_function_name not in functions:
            continue
        # a data line is detected
        match = ConstantPool.DATA_LINE.match(line)
        if match:
            symbol_address = int(match.group(1), 16)
            symbol = None
            if symbol_address in symbols_by_address:
                symbol = symbols_by_address[symbol_address]
            else:
                print "{} of {} is not in symbol table!".format(hex(symbol_address), current_function_name)
            if symbol and not symbol.name.startswith("$") and not symbol.name.startswith("__func__"):
                new_functions[current_function_name].append(symbol)

    return new_functions


def create_symbol_table(binary):
    """Creates symbol table from binary.

    Args:
        binary: Binary which is used.

    Returns:
        Symbols in this binary.

    Raises:
        None
    """
    symbols_by_name = {}
    symbols_by_address = {}
    symtable_found = False
    for line in run_process(ConstantPool.READELF.format(binary)):
        if line.strip().startswith(Symbol.SYMTABLE_START):
            symtable_found = True
        elif line.strip().startswith(Symbol.SYMTABLE_HEADER):
            continue
        elif line.strip():
            symbol = Symbol(line.strip())
            symbols_by_name[symbol.name] = symbol
            symbols_by_address[symbol.address] = symbol

    if not symtable_found:
        print >> stderr, "{} not found in binary {}!".format(Symbol.SYMTABLE_START, binary)

    return symbols_by_name, symbols_by_address


def get_all_sections(binary):
    """Find all section in binary.

    Args:
        binary: Binary which is used.

    Returns:
        Sections in this binary.

    Raises:
        None
    """
    sections_by_nr = {}
    sections_by_name = {}
    for line in run_process(ConstantPool.SECTIONS.format(binary)):
        match = ConstantPool.SECTION_LINE.match(line)
        if match:
            section = Section(match)
            sections_by_name[section.name] = section
            sections_by_nr[section.nr] = section

    return sections_by_name, sections_by_nr


def hash_syms_in_functions(binary, sym_functions, sym_functions_by_addr):
    """Find and hashes symbols in given functions

    Args:
        binary: Binary which is used.
        sym_functions: Functions to consider.

    Returns:
        Checksum of symbols in the given functions.

    Raises:
        None
    """
    symbols_by_name, symbols_by_address = create_symbol_table(binary)
    sections_by_name, sections_by_nr = get_all_sections(binary)
    all_functions = get_symbols_in_functions(sym_functions, sym_functions_by_addr, symbols_by_address, binary)

    sym_hashes = defaultdict(dict)

    with open(binary, "rb") as bin:
            for a_function, symbols_list in all_functions.iteritems():
                for sym in symbols_list:
                    #print >> f, "    addr: {} name: {} scope: {} size: {}".format(sym.address, sym.name, sym.bind, sym.size),
                    section_nr = sym.ndx
                    try:
                        section_nr = int(section_nr)
                    except ValueError:
                        #print >> f," section: NONE[nr={}]".format(section_nr)
                        continue
                    section = sections_by_nr[section_nr]
                    #print >> f, " section: {}".format(section.name),
                    file_offset = section.addr2off(sym.address)
                    #print >> f, " file_offset: {}".format(hex(file_offset)),
                    bin.seek(file_offset)
                    if section.name != ".bss":
                        data_checksum = zlib.adler32(bin.read(sym.size))
                    else:
                        data_checksum = 1
                    sym_hashes[a_function][sym.name] = data_checksum
                    #print >> f, " data_checksum: {}".format(hex(data_checksum))

    return sym_hashes
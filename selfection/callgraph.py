#!/usr/bin/env python

import argparse
import os
from collections import defaultdict

import zlib

from Graph import Graph
from Symbol import Function, Symbol
from parser import get_callgraph, get_test_functions, get_all_functions, create_symbol_table, get_symbols_in_functions, \
    get_all_sections, hash_syms_in_functions
from persistence import makedirs, load, save


def rts(args):
    binary = args.binary
    cache_dir = args.dir
    skip_path = args.skip

    # create path of skipped functions file
    makedirs(os.path.dirname(skip_path))
    # make cache dir
    makedirs(cache_dir)

    # Read the previous state
    callgraph_filepath = os.path.join(cache_dir, "graph.pickle")
    functions_filepath = os.path.join(cache_dir, "functions.pickle")

    test_functions_file = os.path.join(cache_dir, "all_test_functions.txt")
    new_test_functions_file = os.path.join(cache_dir, "test_functions.txt")

    affected_functions_file = os.path.join(cache_dir, "affected_functions.txt")
    modified_new_functions_file = os.path.join(cache_dir, "modified_new_functions.txt")

    test_functions = set()
    if os.path.isfile(test_functions_file):
        with open(test_functions_file, 'r') as f:
            for line in f:
                test_functions.add(line.rstrip())

    if os.path.isfile(new_test_functions_file):
        with open(new_test_functions_file, 'r') as f:
            for line in f:
                test_functions.add(line.rstrip())

    old_callgraph = Graph()
    if os.path.isfile(callgraph_filepath):
        old_callgraph.read(callgraph_filepath)

    old_functions = defaultdict(lambda: 1)
    if os.path.isfile(functions_filepath):
        old_functions = Function.read(functions_filepath)

    sym_functions, sym_functions_by_addr = get_all_functions(binary)
    # Get the current state
    callgraph, functions = get_callgraph(sym_functions, binary)

    # Find the change
    modified_new_functions, skipped_functions = Function.diff(old_functions, functions)

    # Find change due to symbols
    if args.syms:
        sym_functions_file = os.path.join(cache_dir, "syms.pickle")
        old_syms_functions = {}
        if os.path.isfile(sym_functions_file):
            old_syms_functions = load(sym_functions_file)
        new_syms_functions = hash_syms_in_functions(binary, sym_functions, sym_functions_by_addr)
        functions_with_modified_vars = Symbol.diff(old_syms_functions, new_syms_functions)
        save(new_syms_functions, sym_functions_file)
        modified_new_functions |= functions_with_modified_vars
        skipped_functions -= functions_with_modified_vars

    # Find affected tests by the change
    affected_tests = Graph.find_affected_tests(callgraph, modified_new_functions)

    if args.debug:
        with open(affected_functions_file, "w") as f:
            for function in affected_tests:
                print >> f, function

        with open(modified_new_functions_file, "w") as f:
            for function in modified_new_functions:
                print >> f, function

    with open(skip_path, "w") as f:
        for test_function in test_functions:
            if test_function not in affected_tests:
                print >> f, test_function

    # Execute affected tests later

    # Save state
    callgraph.write(callgraph_filepath)
    Function.write(functions, functions_filepath)
    with open(test_functions_file, "w") as f:
        for test_function in test_functions:
            print >> f, test_function

def main():
    parser = argparse.ArgumentParser(description='Generate callgraph from ELF binary and do selection on the graph', prog="TOOL")
    subparsers = parser.add_subparsers(help="command help", dest='command')

    parser_rts = subparsers.add_parser("rts", help="rts help")
    parser_rts.add_argument("binary", metavar='BINARY', type=str, help='binary file')
    parser_rts.add_argument('--dir', default=".ekstazi", type=str, help="cache directory for dependencies")
    parser_rts.add_argument('--skip', default="skip.diff", type=str, help="file path of skipped functions")
    parser_rts.add_argument('--debug', default=False, action='store_true', help="Enable debug output")
    parser_rts.add_argument('--syms', default=False, action='store_true', help="Enable tracking of symbols")

    args = parser.parse_args()

    if args.command == "rts":
        rts(args)
    else:
        parser.help()

if __name__ == '__main__':
    main()

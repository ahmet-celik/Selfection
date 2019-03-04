from collections import defaultdict, deque
from ConstantPool import ConstantPool
from persistence import save
from persistence import load


class Graph(object):

    def __init__(self):
        self.edges = defaultdict(set)

    def add_edge(self, _from, _to):
        self.edges[_from].add(_to)

    def reverse_graph(self):
        """Reverse edges of given directed graph.

        Args:
            graph: Graph represented using adjacency lists.

        Returns:
            Graph with reversed edges.

        Raises:
            None
        """
        reverse = Graph()

        for _from, _to in self.edges.iteritems():
            for _from_prime in _to:
                reverse.add_edge(_from_prime, _from)

        return reverse

    def __getitem__(self, node):
        """Get adjacency list of this node

        Args:
            node: Node from graph

        Returns:
            Adjacent nodes

        Raises:
            None
        """
        return self.edges[node]

    def read(self, filename):
        """Reads graph from file with given filename

        Args:
            filename: Name of file which graph is stored

        Returns:
            Graph object

        Raises:
            None
        """
        self.edges = load(filename)

    def write(self, filename):
        """Writes graph to file with given filename

        Args:
            filename: Name of file which graph is going to be stored

        Return:
            None

        Raises:
            None
        """
        save(self.edges, filename)

    def transitive_closure(self, start, filter_function=lambda x: True, cut_function=lambda x: False):
        closure = set()
        visited = set()
        to_visit = deque(start)
        while to_visit:
            current = to_visit.popleft()
            if current in visited:
                continue
            if filter_function(current):
                closure.add(current)
            if current in self.edges and not cut_function(current):  # and current != "printf":  # many deps added because of printf
                to_visit.extend(self.edges[current])
            visited.add(current)
        return closure

    def is_leaf_test(self, test):
        if test in self.edges:
            for f in self.edges[test]:
                if ConstantPool.FUNC_TEST.match(f):
                    return False
        return True

    @staticmethod
    def find_affected_tests(graph, changed_functions):
        """Finds all affected tests if a function in changed_functions are modified.

        Args:
            graph: Call graph from caller to callee.
            all_functions: A list of all functions.
            changed_functions: A list of modified functions.

        Returns:
            Affected test functions

        Raises:
            None
        """
        depends_on = graph.reverse_graph()

        return depends_on.transitive_closure(changed_functions, lambda f: ConstantPool.FUNC_TEST.match(f))

from parse import trim_and_split_explain_result


class Node:
    def __init__(
        self, name, estRows, task, accessObject, operatorInfo, level, children=None
    ):
        self.name = name
        self.estRows = estRows
        self.task = task
        self.accessObject = accessObject
        self.operatorInfo = operatorInfo
        self.level = level
        self.children = children or []

    def add_child(self, child):
        self.children.append(child)


def build_tree(lines):
    root = Node("root", None, None, None, None, -1)
    stack = [root]
    for line in lines:
        cols = line.split("|")[1:-1]
        name = cols[0].strip()
        estRows = cols[1].strip()
        task = cols[2].strip()
        accessObject = cols[3].strip()
        operatorInfo = cols[4].strip()
        level = line.find(name) // 2
        node = Node(name, estRows, task, accessObject, operatorInfo, level)
        if level > stack[-1].level:
            stack[-1].add_child(node)
            stack.append(node)
        else:
            while level <= stack[-1].level:
                stack.pop()
            stack[-1].add_child(node)
            stack.append(node)
    return root


def preorder_traversal(root):
    result = []
    stack = [(root, [])]
    while stack:
        node, path = stack.pop()
        if node.name != "root":
            result.append(
                (
                    node.name,
                    node.estRows,
                    node.task,
                    node.accessObject,
                    node.operatorInfo,
                )
            )
        path.append(node)
        stack.extend([(child, path[:]) for child in reversed(node.children)])
    return result


if __name__ == "__main__":
    explain_lines = """
        +------------------------------+----------+-----------+---------------+--------------------------------------------+
        | id                           | estRows  | task      | access object | operator info                              |
        +------------------------------+----------+-----------+---------------+--------------------------------------------+
        | HashJoin_22                  | 12487.50 | root      |               | inner join, equal:[eq(test.t.a, test.t.b)] |
        | ├─TableReader_26(Build)      | 9990.00  | root      |               | data:Selection_25                          |
        | │ └─Selection_25             | 9990.00  | cop[tikv] |               | not(isnull(test.t.b))                      |
        | │   └─TableFullScan_24       | 10000.00 | cop[tikv] | table:t1      | keep order:false, stats:pseudo             |
        | └─TableReader_29(Probe)      | 9990.00  | root      |               | data:Selection_28                          |
        |   └─Selection_28             | 9990.00  | cop[tikv] |               | not(isnull(test.t.a))                      |
        |     └─TableFullScan_27       | 10000.00 | cop[tikv] | table:t2      | keep order:false, stats:pseudo             |
        +------------------------------+----------+-----------+---------------+--------------------------------------------+
    """
    explain_lines = trim_and_split_explain_result(explain_lines)
    lines = explain_lines[3 : len(explain_lines) - 1]
    print(lines)

    # lines = [line for line in explain_lines.split("\n") if line.strip()]

    # print(lines)
    tree = build_tree(lines[2:-2])

    nodes = preorder_traversal(tree)
    for node in nodes:
        print(node)

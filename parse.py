import json


def is_separate_line(line):
    line = line.strip()
    if len(line) == 0:
        return False
    for c in line:
        if c != "+" and c != "-":
            return False
    return True


def trim_and_split_explain_result(explain_result):
    lines = explain_result.split("\n")
    idx = [0, 0, 0]
    p = 0
    for i in range(len(lines)):
        if is_separate_line(lines[i]):
            idx[p] = i
            p += 1
            if p == 3:
                break
    if p != 3:
        return None, Exception("invalid explain result")

    return lines[idx[0] : idx[2] + 1]


def split_rows(rows):
    results = []
    for row in rows:
        cols = row.split("|")
        cols = [c.strip().replace("└─", "") for c in cols[1:-1]]
        results.append(cols)
    return results


def parse_text(explain_text):
    explain_lines = trim_and_split_explain_result(explain_text)
    rows = split_rows(explain_lines[3 : len(explain_lines) - 1])
    result = {}
    for row in rows:
        id_name = row[0]
        est_rows = float(row[1])
        other_info = row[2:]
        result[id_name] = [est_rows, other_info]

    return json.dumps(result)


explain_text = """
+-------------------------+----------+-----------+---------------+--------------------------------+
| id                      | estRows  | task      | access object | operator info                  |
+-------------------------+----------+-----------+---------------+--------------------------------+
| TableReader_7           | 10.00    | root      |               | data:Selection_6               |
| └─Selection_6           | 10.00    | cop[tikv] |               | eq(test.t.c, 10)               |
|   └─TableFullScan_5     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo |
+-------------------------+----------+-----------+---------------+--------------------------------+
"""


print(parse_text(explain_text))

# output:
# {"TableReader_7": [10.0, ["root", "", "data:Selection_6"]], "Selection_6": [10.0, ["cop[tikv]", "", "eq(test.t.c, 10)"]], "TableFullScan_5": [10000.0, ["cop[tikv]", "table:t", "keep order:false, stats:pseudo"]]}

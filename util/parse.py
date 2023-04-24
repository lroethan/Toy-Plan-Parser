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
        raise Exception("invalid explain result")

    return lines[idx[0] : idx[2] + 1]


def split_rows(rows):
    results = []
    for row in rows:
        cols = row.split("|")
        cols = [
            c.strip().replace("└─", "").replace("├─", "").replace("│", "").strip()
            for c in cols[1:-1]
        ]
        if cols and any(
            s in cols[0].lower()
            for s in [
                "top",
                "scan",
                "join",
                "agg",
                "sort",
                "group",
            ]  # Index relevant operators
        ):
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

print(parse_text(explain_text))


# explain_text = """
# 	+--------------------------+----------+------+--------------------------------------------------------------------+
# 	| id                       | count    | task | operator info                                                      |
# 	+--------------------------+----------+------+--------------------------------------------------------------------+
# 	| HashLeftJoin_13          | 12487.50 | root | inner join, inner:TableReader_17, equal:[eq(test.t1.a, test.t2.b)] |
# 	| ├─TableReader_20         | 9990.00  | root | data:Selection_19                                                  |
# 	| │ └─Selection_19         | 9990.00  | cop  | not(isnull(test.t1.a))                                             |
# 	| │   └─TableScan_18       | 10000.00 | cop  | table:t2, range:[-inf,+inf], keep order:false, stats:pseudo        |
# 	| └─TableReader_17         | 9990.00  | root | data:Selection_16                                                  |
# 	|   └─Selection_16         | 9990.00  | cop  | not(isnull(test.t2.b))                                             |
# 	|     └─TableScan_15       | 10000.00 | cop  | table:t1, range:[-inf,+inf], keep order:false, stats:pseudo        |
# 	+--------------------------+----------+------+--------------------------------------------------------------------+
# """

# original output:
# {
#     "HashLeftJoin_13": [12487.5, ["root", "inner join, inner:TableReader_17, equal:[eq(test.t1.a, test.t2.b)]"]],
#     "TableReader_20": [9990.0, ["root", "data:Selection_19"]],
#     "Selection_19": [9990.0, ["cop", "not(isnull(test.t1.a))"]],
#     "TableScan_18": [10000.0, ["cop", "table:t2, range:[-inf,+inf], keep order:false, stats:pseudo"]],
#     "TableReader_17": [9990.0, ["root", "data:Selection_16"]],
#     "Selection_16": [9990.0, ["cop", "not(isnull(test.t2.b))"]],
#     "TableScan_15": [10000.0, ["cop", "table:t1, range:[-inf,+inf], keep order:false, stats:pseudo"]]
# }

# output:
# {
#     "HashLeftJoin_13": [12487.5, ["root", "inner join, inner:TableReader_17, equal:[eq(test.t1.a, test.t2.b)]"]],
#     "TableScan_18": [10000.0, ["cop", "table:t2, range:[-inf,+inf], keep order:false, stats:pseudo"]],
#     "TableScan_15": [10000.0, ["cop", "table:t1, range:[-inf,+inf], keep order:false, stats:pseudo"]]
# }

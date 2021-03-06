import sqlite3
from typing import Union, List, Tuple, Set


class Conwrapper():
    def __init__(self, db_path: str):
        self.con = sqlite3.connect(db_path)
        self.cursor = self.con.cursor()

    def __enter__(self):
        return self.con, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()
        return exc_type is None


def sanitize(data: Union[object, List[object], Tuple[object]]) -> Union[str, List[str], Tuple[str]]:
    def sanatize_single(single_data: object) -> str:
        sanitized = str(single_data)
        sanitized = sanitized.replace("'", "''")
        if isinstance(single_data, str):
            sanitized = f"'{sanitized}'"  # SQL wraps strings in quotes
        return sanitized

    if isinstance(data, (list, tuple)):
        for i in range(len(data)):
            data[i] = sanatize_single(data[i])
        return data
    else:
        return sanatize_single(data)


def create_entry_string(data: Union[object, List[object]], skip_sanitize: bool = False) -> str:
    if isinstance(data, Set):
        data = list(data)
    if isinstance(data, (List, Tuple)):
        temp = []  # in the case of tuples, we cant assign back to data, so we use temp instead
        for i in range(len(data)):
            if skip_sanitize:
                temp.append(data[i])
            else:
                temp.append(sanitize(data[i]))
        return f"({','.join(temp)})"
    else:
        if skip_sanitize:
            return f"({data})"
        else:
            return f"({sanitize(data)})"


def create_value_string(values: Union[object, List[object], List[List[object]]]) -> str:
    if isinstance(values, (List, Tuple)):
        values = values.copy()
        for i in range(len(values)):
            values[i] = create_entry_string(values[i])
    else:
        values = create_entry_string(values)
    return ','.join(values)


def convert_tuple_to_list(values: List[Tuple[object]]) -> List[object]:
    result = []
    for (value,) in values:
        result.append(value)
    return result

ROMAN_NUMERALS = [
    ("M", 1000),
    ("CM", 900),
    ("D", 500),
    ("CD", 400),
    ("C", 100),
    ("XC", 90),
    ("L", 50),
    ("XL", 40),
    ("X", 10),
    ("IX", 9),
    ("V", 5),
    ("IV", 4),
    ("I", 1),
]


def to_roman(num: int) -> str:
    result = ""
    for roman, value in ROMAN_NUMERALS:
        while num >= value:
            result += roman
            num -= value
    return result


def sort_order_to_row_col(sort_order: int, cols: int) -> tuple[int, int]:
    """Pretvori linearni sort_order (0-based) u (row, col) 1-based."""
    row = sort_order // cols + 1
    col = sort_order % cols + 1
    return row, col


def flow_index_to_row_col(flow_index: int, cols: int) -> tuple[int, int]:
    """Pozicija u mreži za i-ti korak starog JS flow algoritma (0-based index)."""
    return flow_index // cols + 1, flow_index % cols + 1

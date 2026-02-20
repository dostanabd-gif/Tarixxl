ROSS_308_FCR = {
    7: 0.95,
    14: 1.17,
    21: 1.34,
    28: 1.48,
    35: 1.61,
    42: 1.73,
}

COBB_500_FCR = {
    7: 0.93,
    14: 1.15,
    21: 1.32,
    28: 1.46,
    35: 1.58,
    42: 1.70,
}


def get_reference_fcr(cross: str, day: int) -> float:
    table = ROSS_308_FCR if cross.lower() == "ross-308" else COBB_500_FCR
    nearest_day = min(table.keys(), key=lambda d: abs(d - day))
    return table[nearest_day]

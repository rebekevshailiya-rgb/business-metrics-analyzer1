def calculate_profitability(revenue: float, cost: float) -> float:
    if revenue == 0:
        return 0.0
    return (revenue - cost) / revenue * 100

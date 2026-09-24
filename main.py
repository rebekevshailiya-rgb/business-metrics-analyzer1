import pandas as pd
import matplotlib.pyplot as plt


def calculate_profitability(revenue: float, cost: float) -> float:
    """Возвращает рентабельность в процентах."""
    if revenue == 0:
        return 0.0
    return (revenue - cost) / revenue * 100


def main():
    data = {
        "Месяц": ["Январь", "Февраль", "Март"],
        "Выручка": [120000, 150000, 135000],
    }

    df = pd.DataFrame(data)

    print(df)
    print("Средняя выручка:", df["Выручка"].mean())

    revenue = 150000
    cost = 100000
    profitability = calculate_profitability(revenue, cost)
    print(f"Рентабельность: {profitability:.2f}%")

    plt.plot(df["Месяц"], df["Выручка"], marker="o")
    plt.title("Динамика выручки")
    plt.xlabel("Месяц")
    plt.ylabel("Выручка, руб.")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()

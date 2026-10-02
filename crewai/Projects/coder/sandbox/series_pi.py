from decimal import Decimal, getcontext


def calculate_pi_like_series(terms: int) -> Decimal:
    getcontext().prec = 50
    total = Decimal(0)
    sign = 1
    for i in range(terms):
        denominator = 2 * i + 1
        total += Decimal(sign) / Decimal(denominator)
        sign *= -1
    return total * 4


if __name__ == '__main__':
    result = calculate_pi_like_series(1_000_000)
    print(result)

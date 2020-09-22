#
def differentiate(numbers):
    """
    Perform differentiation on a sequence of numbers
    i.e. return the difference between each consecutive number
    assumes 'dt' is constant
    :return:

    """
    diff_numbers = [0]

    if len(numbers) < 2:
        return None

    for i in range(1, len(numbers)):
        dy = numbers[i] - numbers[i-1]
        diff_numbers.append(dy)

    return diff_numbers

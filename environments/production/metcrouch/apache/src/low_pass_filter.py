# https://stackoverflow.com/questions/14884017/how-to-calculate-moving-average-in-python-3
#
from itertools import islice

# enabler functions - no need to call outside this module
def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def moving_averages(values, size):
    for selection in window(values, size):
        yield sum(selection) / size

# -------------------------------------------------------
# the usable function
def low_pass(y, win):
    smoothed = []
    for avg in moving_averages(y, win):
        smoothed.append(avg)
        #print(avg)
    return smoothed

# test harness
def main():
    window_size = 5
    raw_data = [1,2,4,6,4,7,4,6,8,8,8,8,7,7,7,8,6,0,0,0]

    filtered = low_pass(raw_data, window_size)

    print(filtered)

if __name__ == '__main__':
    main()
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# var 18
def find_zero_col_in_mass(mass):
    count_col = 0
    buff = 0
    for i in mass:
        for j in i:
            if j == 0:
                buff = 1
        if buff == 1:
            count_col += 1
        buff = 0
    return count_col


def find_long_line_mass(mass):
    result = 0
    k = 0
    find_less = None
    for i in mass:
        k += 1
        buff = set(i)
        if find_less != None and len(buff) < len(find_less):
            result = k
        else:
            find_less = buff
    return result


# var12
def delete_zero_from_mass(mass):
    ind = 0
    buff = 0
    ind_for_pop = set()
    for m in mass:
        for k in m:
            if k == 0:
                buff = 1
        if buff == 1:
            ind_for_pop.add(tuple(m))
            buff = 0
        ind += 1

    # import pdb;pdb.set_trace()
    return [m for m in mass if tuple(m) not in ind_for_pop]
    # return { "a":m for m in mass if tuple(m) not in ind_for_pop }


def first_positive_line(mass):
    ind = 0
    for m in mass:
        for k in m:
            if k > 0:
                return ind
        ind += 1


mass = [[-1, -1, -1], [0, 7, 67], [0, 2, 0]]

# var 18
print(f'zero columns {find_zero_col_in_mass(mass)}')
print(f'the longest string with the same elements {find_long_line_mass(mass)}')
# var 12
print(f'delete columns with 0 {delete_zero_from_mass(mass)}')
print(f'first line with positive number {first_positive_line(mass)}')

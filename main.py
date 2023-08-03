# var 18
def find_zero_col_in_mass(mass):
    count_col = 0
    for i in mass:
        if 0 in i:
            count_col += 1
    return count_col


def find_long_line_mass(mass):
    count = 0
    buff = None
    answ_list = []
    for indx, val in enumerate(mass):
        answ_list.append(0)
        for i in val:
            if buff is not None:
                if buff == i:
                    count += 1
                else:
                    if count > answ_list[indx]:
                        answ_list[indx] = count
                    count = 0
            buff = i
    return answ_list.index(max(answ_list)) + 1


# var12
def delete_zero_from_mass(mass):
    return [m for m in mass if len(set(tuple(m))) != 1 and set[0] != 0]


def invert_list(mass):
    return list(map(list, zip(*mass)))


def delete_all_zero_from_mass(mass):
    return invert_list(delete_zero_from_mass(invert_list(delete_zero_from_mass(mass))))


def first_positive_line(mass):
    for ind, m in enumerate(mass):
        for k in m:
            if k > 0:
                return ind


mass = [[0, -1, -2, -1], [0, 7, 4, 67], [0, 0, 0, 0], [0, 2, 2, 2]]

# var 18
print(f'zero columns {find_zero_col_in_mass(mass)}')
print(f'the longest string with the same elements {find_long_line_mass(mass)}')
# var 12
print(f'delete columns with 0 {delete_all_zero_from_mass(mass)}')
print(f'first line with positive number {first_positive_line(mass)}')

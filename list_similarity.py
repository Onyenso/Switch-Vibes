# Python3 code to demonstrate working of
# Percentage similarity of lists
# using "|" operator + "&" operator + set()

# initialize lists
test_list1 = [
    "Pete Edocxhie",
    "Theresa Onuozrah",
    "Flavcour",
    "Phynco",
]
test_list2 = [
    "Larry Gaaga",
    "Theresa Onuorah",
    "Flavour",
    "Phyno"
]

# printing original lists
print("The original list 1 is : " + str(test_list1))
print("The original list 2 is : " + str(test_list2))

# Percentage similarity of lists
# using "|" operator + "&" operator + set()
def list_similarity(list_1, list_2):
    result = len(set(list_1) & set(list_2)) / float(len(set(list_1) | set(list_2)))
    return result

# printing result
print("Percentage similarity among lists is : " + str(list_similarity(test_list1, test_list2)))

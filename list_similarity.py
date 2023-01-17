# Python3 code to demonstrate working of
# Percentage similarity of lists
# using "|" operator + "&" operator + set()

# initialize lists
test_list1 = ['ckay', 'focalistic', 'davido', 'abidoza']
test_list2 = ["ckay"]

# printing original lists
print("The original list 1 is : ", test_list1)
print("The original list 2 is : ", test_list2)

# Percentage similarity of lists
# using "|" operator + "&" operator + set()
def list_similarity(list_1, list_2):
    result = len(set(list_1) & set(list_2)) / float(len(set(list_1) | set(list_2)))
    return result

# printing result
print("Percentage similarity among lists is : ", list_similarity(test_list1, test_list2))

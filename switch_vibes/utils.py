import difflib


def string_similarity(str1, str2):
    result =  difflib.SequenceMatcher(a=str1.lower(), b=str2.lower())
    return result.ratio()


def list_similarity(list_1, list_2):
    result = len(set(list_1) & set(list_2)) / float(len(set(list_1) | set(list_2)))
    return result


str1 = "Piano Tribute Players"
str2 = "Troy Smith"
# print(f"string_similarity between {str1} vs {str2} = {string_similarity(str1, str2)}\n")

str1 = [
   "Ariana Grande"
]
str2 = [
    "Karaoke Pro"
]

# print(f"list_similarity between {str1} vs {str2} = {list_similarity(str1,str2)}\n")

# print(f"string_similarity between {str(str1)} vs {str(str2)} = {string_similarity(str(str1), str(str2))}\n")
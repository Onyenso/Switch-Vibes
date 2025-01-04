import difflib


def string_similarity(str1, str2):
    result =  difflib.SequenceMatcher(a=str1.lower(), b=str2.lower())
    return result.ratio()


def list_similarity(list_1, list_2):
    result = len(set(list_1) & set(list_2)) / float(len(set(list_1) | set(list_2)))
    return result

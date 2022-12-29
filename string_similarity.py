import difflib


def string_similarity(str1, str2):
    result =  difflib.SequenceMatcher(a=str1, b=str2,)
    return result.ratio()


str1 = "Kiss Daniel"
str2 = "Kizz Daniel"
print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")

str1 = "Ariana Grande ft. Nicki Minaj"
str2 = "Ariana Grande"
print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")

str1 = "M. I Abaga"
str2 = "M. I. Abaga"
print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")

str1 = "Asa"
str2 = "A\u1e63a"
print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")

str1 = "ZAYN & Taylor Swift"
str2 = "ZAYN"
print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")

str1 = "DJ Spinnall"
str2 = "DJ Spinnal"
print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")

str1 = "Sarkodie Ft.Oxlade"
str2 = "Sarkodie"
print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")

str1 = [
    "Pete Edochie",
    "Theresa Onuorah",
    "Flavour",
    "Phyno",
]
str2 = [
    "Larry Gaaga",
    "Theresa Onuorah",
    "Flavour",
    "Phyno"
]

print(f"{str1} vs {str2} = {string_similarity(str1,str2)}\n")
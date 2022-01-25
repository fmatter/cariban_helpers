from pycldf import Generic
import os
import itertools
from download import download
from segments import Tokenizer, Profile


home = os.path.expanduser('~')
dataset_path = os.path.join(home, ".cldf/cariban_meta")
metadata_path = os.path.join(dataset_path, "cldf/metadata.json")

def download_dataset():
    download_path = download("https://github.com/fmatter/cariban_meta/releases/download/v0.0.5/cariban_meta.zip", dataset_path, kind="zip", replace=True)

if not os.path.isfile(metadata_path):
    download_dataset()

c_data = Generic.from_metadata(metadata_path)

glottocodes = {}
shorthands = {}
lang_ids = {}
isos = {}
dialects = {}
language_data = {}
extant_languages = []
proto_languages = []
top_languages = ["PPar", "PTar", "PPek", "PPP", "PPem", "PMan", "uxc", "way", "apa", "kar", "wmr", "yuk", "mak"]
for lg in c_data["LanguageTable"]:
    glottocodes[lg["Glottocode"]] = {
        "shorthand": lg["Shorthand"],
        "id": lg["ID"],
        "name": lg["Name"]
    }
    
    shorthands[lg["Shorthand"]] = {
        "id": lg["ID"],
        "name": lg["Name"],
        "glottocode": lg["Glottocode"]
    }
    
    lang_ids[lg["ID"]] = {
        "shorthand": lg["Shorthand"],
        "name": lg["Name"],
        "glottocode": lg["Glottocode"]
    }
    language_data[lg["ID"]] = lg
    
    if lg["Dialect_Of"] != None:
        dialects[lg["ID"]] = lg["Dialect_Of"]
    else:
        dialects[lg["ID"]] = lg["ID"]

    if lg["Proto_Language"]:
        proto_languages.append(lg["ID"])
    else:
        extant_languages.append(lg["ID"])

def get_lg_data(id):
    return language_data[id]

def get_glottocode(string):
    for map in [shorthands, lang_ids]:
        if string in map:
            return map[string]["glottocode"]
            
def get_shorthand(string):
    for map in [glottocodes, lang_ids]:
        if string in map:
            return map[string]["shorthand"]
            
def get_name(string):
    for map in [glottocodes, shorthands, lang_ids]:
        if string in map:
            return map[string]["name"]
            
def get_lg_id(string):
    for map in [glottocodes, shorthands, isos]:
        if string in map:
            return map[string]["id"]

def dedialectify(string):
    orig = string
    if string in lang_ids:
        return dialects[string]
    else:
        dialect_id = dialects[get_lg_id(string)]
        if orig in glottocodes:
            return get_glottocode(dialect_id)
        elif orig in shorthands:
            return get_shorthand(dialect_id)

segs = """p
t
k
b
d
g
m
n
ŋ
ɸ
s
ʃ
t͡ʃ
a
e
i
o
ɨ
ə
u
ẽ
õ
ũ
ã
ə̃
ɨ̃
ĩ
ɣ
f
rʲ
l
r
w
j
ɟ
h
ʔ
V
aa
ee
ii
oo
uu
ɨɨ
əə
ɲ
z
ʒ""".split("\n")

segment_list = [{"Grapheme": x, "mapping": x} for x in segs]
tokenizer = Tokenizer(Profile(*segment_list))

def segmentify(str):
    rem = ["[", "]", "-", "="]
    for i in rem:
        str = str.replace(i, "")
    return tokenizer(str)


lists = {
    "glottocode": get_glottocode,
    "shorthand": get_shorthand,
    "id": get_lg_id,
    "name": get_name
}  


def lg_order(identifier="id", as_dict=True):
    order = ["PC", "PPar", "kax", "PWai", "hix", "wai", "PPek", "PXin", "ara", "ikp", "bak", "PTar", "PTir", "tri", "aku", "car", "way", "apa", "kar", "mak", "PPP", "PPem", "kap", "aka", "ing", "pat", "pem", "mac", "pan", "tam", "PMan", "yab", "map", "pno", "cum", "uxc", "kui", "yuk", "jap", "wmr"]
    if identifier != "id":
        order = list(map(lists[identifier], order))
    if as_dict:
        numbers = list(range(0,len(order)))
        return dict(zip(order, numbers))
    else:
        return order

import re
separators = ["-", "=", "<", ">"]

def deparentify(full_string, par="("):
    if par == "(":
        par2 = ")"
    elif par == "[":
        par2 = "]"
    all_variants = []
    def iterate(string):
        for repl in [r"\1", ""]:
            if par == "(":
                variant = re.sub(rf"\((.*?)\)", repl, string, 1)
            elif par == "[":
                variant = re.sub(rf"\[(.*?)\]", repl, string, 1)
            if (par in variant):
                for i in iterate(variant):
                    yield i
            else:
                yield variant.replace(par2, "")

    for substring in full_string.split(" / "):
        all_variants.extend(list(itertools.chain(*[iterate(s) for s in substring.split(", ")])))
    seen = set()
    return [x for x in all_variants if not (x in seen or seen.add(x))]


# def extract_allomorphs(full_string):
#     portions = full_string.split("/")
#     found_allomorphs = []
#     def iter_parens(string):
#         lose = re.sub("\((.*?)\)", r"\1", string, 1)
#         keep = re.sub("\((.*?)\)", "", string, 1)
#         if "(" in lose:
#             iter_parens(lose)
#         else:
#             found_allomorphs.append(lose)
#         if "(" in keep:
#             iter_parens(keep)
#         else:
#             found_allomorphs.append(keep)
#     for string in portions:
#         iter_parens(string)
#     return list(dict.fromkeys(found_allomorphs))

# def merge_allomorphs(form, as_list=False):
#     if as_list:
#         if form in [[], [""], [" "]]: return form
#         allomorphs = form
#     else:
#         if form in ["", " "]: return form
#         allomorphs = form.split("; ")
#     if allomorphs[0][-1] in separators:
#         prefix = True
#         suffix = False
#     elif allomorphs[0][0] in separators:
#         prefix = False
#         suffix = True
#     else:
#         prefix = False
#         suffix = False
#     allomorphs.sort(key=len)
#     #We take the shortest allomorph as the base
#     new_allomorphs = [allomorphs[0]]
#     #Then we iterate the longer allomorphs
#     for allomorph in allomorphs[1:]:
#         #If there is an affricate, let's just add it straight away, we don't want to split these up
#         if "͡" in allomorph:
#             new_allomorphs.append(allomorph)
#             continue
#         found_hit = False
#         #We iterate the allomorphs we already added to the new form
#         for i, existing_allomorph in enumerate(new_allomorphs):
#             # if found_hit:
#             #     print("Aborting…")
#             if not found_hit:
#                 # print("Looking at candidate %s, comparing it with %s" % (allomorph, existing_allomorph))
#                 if prefix:
#                     right_border = len(allomorph)-2
#                 else:
#                     right_border = len(allomorph)-1
#                 if suffix:
#                     left_border = 1
#                 else:
#                     left_border = 0
#                 for right_edge in range(right_border, -1, -1):
#                     for left_edge in range(left_border, right_edge+1):
#                         if left_edge == right_edge:
#                             allo_slice = allomorph[left_edge]
#                         else:
#                             allo_slice = allomorph[left_edge:right_edge+1]
#                         if suffix:
#                             preserve = existing_allomorph[1::]
#                         elif prefix:
#                             preserve = existing_allomorph[0:-1]
#                         else:
#                             preserve = existing_allomorph
#                         # comp = preserve.replace("(","").replace(")","")
#                         comp = preserve
#                         # print(f"Comparing {allo_slice} with {comp} [{left_edge}:{right_edge}]")
#                         if allo_slice == comp:
#                             # print(f"Got a hit! {allo_slice} in position {left_edge}:{right_edge} of {allomorph} is identical to {comp} ({existing_allomorph})")
#                             new_allomorph = "(" + allomorph[:left_edge] + ")" + preserve + "(" + allomorph[right_edge+1:] + ")"
#                             new_allomorph = new_allomorph.replace("-)", ")-")
#                             new_allomorph = new_allomorph.replace("()","")
#                             new_allomorphs[i] = new_allomorph
#                             # print(new_allomorphs)
#                             found_hit = True
#         if not found_hit:
#             # print("No match found between %s and %s" % (allomorph, existing_allomorph))
#             new_allomorphs.append(allomorph)
#     for i, new_allomorph in enumerate(new_allomorphs):
#         for j, other_allomorph in enumerate(new_allomorphs):
#             if i != j:
#                 if new_allomorph in extract_allomorphs(other_allomorph):
#                     # print(f"removing {new_allomorph}, as it is an allomorph of {other_allomorph}")
#                     new_allomorphs.remove(new_allomorph)
#     if as_list:
#         return new_allomorphs
#     else:
#         return "; ".join(new_allomorphs)
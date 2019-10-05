import scholarly
import requests
import json
import csv
from fuzzywuzzy import fuzz

search = scholarly.search_author('Ludo Waltman')
author = next(search).fill()
def levenshtein_check(title, publications):
    for pub in publications:
        comparison = pub.bib["title"]
        # Fetch the citation count from google to return and later compare with scopus
        cite_count = 0
        try:
            cite_count = pub.citedby
        except AttributeError:
            # 0 citations
            pass
        if fuzz.ratio(title.lower(), comparison.lower()) > 90:
            #print("Possible match. " + title + " === " + comparison)
            return cite_count if cite_count else True
    return False

# From the exported scopus publications, check if they exist on scholar
scopus_count = not_found_on_scholar = problematic_scholar = 0
citation_comparisons = []
missing_publications = []
with open("scopus.csv", encoding='utf-8-sig') as csv_file:
    csv_read = csv.DictReader(csv_file)
    for row in csv_read:
        scopus_count += 1
        cite_count = levenshtein_check(row['Title'], author.publications)
        # Could not find the publication on scholar
        if not cite_count:
            not_found_on_scholar += 1
            #print("Manual check if Scholar has the following: " + row['Title'])
            # Check if the missing publication would affect google scholar's h-index
            if row['Cited by'] and int(row['Cited by']) > author.hindex:
                problematic_scholar += 1
                missing_publications.append([row['Title'], row['Cited by']])
        else:
            if isinstance(cite_count, bool):
                cite_count = 0
            scopus_cite = row['Cited by'] if row['Cited by'] else 0
            citation_comparisons.append([cite_count, int(scopus_cite)])

print(str(len(author.publications)) + " publications were found for this Scholar on Google.")
print(str(scopus_count) + " publications were found for this Scholar from the Scopus export.")
print(str(not_found_on_scholar) + " publications on Scopus were not found on Scholar.")
print(str(scopus_count - not_found_on_scholar) + " publications are common across both databases.")
# Calculating the number of papers present on scholar but not scopus -- Total scholar publications minus the common publications (total scopus count - not found on scholar)
print(str(len(author.publications) - (scopus_count - not_found_on_scholar)) + " publications on Scholar were not found on Scopus.")
print(str(problematic_scholar) + " publications on Scopus were not found on Scholar which may affect the h-index.")

# Stored as [ [Title, Cite_Count] ]
for miss in missing_publications:
    print("\""+ str(miss[0]) + "\" is a missing publication from scholar with a citation count that may affect the total h-index of Google Scholar. The citation count of this article is " + str(miss[1]))
    # Check if the missing articles are indexed by Google Scholars search
    # search_query = scholarly.search_pubs_query("Ludo Waltman " + miss[0])
    # try:
    #     authors = next(search_query).fill().bib['author']
    #     print(authors)
    #     if "ludo" in authors.lower() or "waltman" in authors.lower():
    #         print("Google Scholars search engine was able to locate the publication: \"" + miss[0] + "\"\n")
    #     else:
    #         print("Google Scholar could not find: \"" + miss[0] + "\"\n")
    # except StopIteration:
    #     print("--- Nothing was found. You're probably rate-limited by Google, check manually ---")

for counts in citation_comparisons:
    if counts[0] <= counts[1]:
    #    print(str(counts[0]) + " -- " + str(counts[1]))
        pass

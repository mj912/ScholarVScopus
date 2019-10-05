import scholarly
import requests
import json
import csv
from fuzzywuzzy import fuzz

search = scholarly.search_author('Ludo Waltman')
author = next(search).fill()

print(str(len(author.publications)) + " publications were found for this Scholar on Google.");

def levenshtein_check(title, publications, scopus_pubs=False):
    for pub in publications:
        # Scholar pubs accesed by pub.bib['title'] and Scopus pubs accessed by pub['Title']
        comparison = pub['Title'] if scopus_pubs else pub.bib['title']
        if fuzz.ratio(title.lower(), comparison.lower()) > 80:
            #print("Possible match. " + title + " === " + comparison)
            return True
    return False

# From the exported scopus publications, check if they exist on scholar
not_found_on_scholar = 0
problematic_scholar = 0
not_found_on_scopus = 0
with open("scopus.csv", encoding='utf-8-sig') as csv_file:
    csv_read = csv.DictReader(csv_file)
    for row in csv_read:
        if row['Title'].lower() not in [pub.bib['title'].lower() for pub in author.publications]:
            if not levenshtein_check(row['Title'], author.publications):
                not_found_on_scholar += 1
                #print("Manual check if Scholar has the following: " + row['Title'])
                # Check if the missing publication would affect google scholar's h-index
                if row['Cited by'] and int(row['Cited by']) > author.hindex:
                    problematic_scholar += 1
                    print("\""+ row['Title'] + "\" is a missing publication from scholar with a h-index that may affect the total h-index of Google Scholar. The citation count of this article is " + row['Cited by'] + "\n")

    for pub in author.publications:
        csv_file.seek(0)
        if pub.bib['title'].lower() not in [row['Title'].lower() for row in csv_read]:
            csv_file.seek(0)
            if not levenshtein_check(pub.bib['title'], csv_read, True) :
                not_found_on_scopus += 1
                #print("Manual check if Scopus has the following: " + pub.bib['title'])
                
print(str(not_found_on_scholar) + " publications on Scopus were not found on Scholar.")
print(str(not_found_on_scopus) + " publications on Scholar were not found on Scopus.")

print(str(problematic_scholar) + " publications on Scopus were not found on Scholar which may affect the h-index.")

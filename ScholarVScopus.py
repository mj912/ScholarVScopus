'''ScholarVScopus.py:

Michael Johnson CSCI318
Python script written to utilise https://pypi.org/project/scholarly/ module as a means of identifying the differences of an academics Scholar profile in comparison to their Google Scholar profile.
'''
import scholarly
import requests
import json
import csv
import os
from fuzzywuzzy import fuzz

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
            return cite_count if cite_count else True
    return False

# From the exported scopus publications, check if they exist on scholar
def comparisons(filename, author):
    scopus_count = hindex_count = 0
    citation_comparisons = []
    problematic_publications = []
    missing_publications = []
    with open(filename, encoding="utf-8-sig") as csv_file:
        csv_read = csv.DictReader(csv_file)
        for row in csv_read:
            scopus_count += 1
            cite_count = levenshtein_check(row['Title'], author.publications)
            # Could not find the publication on scholar
            if not cite_count:
                missing_publications.append(row["Title"])
                # print("Manual check if Scholar has the following: " + row['Title'])
                # Check if the missing publication would affect google scholar's h-index
                if row['Cited by'] and int(row['Cited by']) > author.hindex:
                    problematic_publications.append([row['Title'], row['Cited by']])
            else:
                if isinstance(cite_count, bool):
                    cite_count = 0
                scopus_cite = row['Cited by'] if row['Cited by'] else 0
                citation_comparisons.append([cite_count, int(scopus_cite)])

    return scopus_count, citation_comparisons, problematic_publications, missing_publications

# Used to count the h-index from the citation counts array. GScholar is index 0
def calculate_hindex(publications):
    publications_sorted = []
    for pub in publications:
        try:
            cite_count = pub.citedby
            publications_sorted.append(cite_count)
        except AttributeError:
            pass
    publications_sorted.sort(reverse=True)

    j = hindex = 0
    while j < len(publications_sorted):
        if publications_sorted[j] > hindex:
            hindex = hindex + 1
        else:
            break
        j = j+1
    return hindex

def write_citation_counts(author_name, citation_comparisons):
    # Saving the citation comparisons to a new directory
    if not os.path.exists(author_name):
        os.mkdir(author_name)
    with open(author_name + "/citation_counts.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        csv_data = [["Google Scholar", "Scopus"]]
        csv_data.extend(citation_comparisons)
        writer.writerows(csv_data)

def write_missing_publications(author_name, missing_publications):
    if not os.path.exists(author_name):
        os.mkdir(author_name)
    with open(author_name + "/missing_publications.txt", "w") as file:
        file.write("\n".join(missing_publications))

def main():
    author_name = input("Enter the search term to identify your Scholar (e.g Ludo Waltman Leiden University): ")
    search = scholarly.search_author(author_name)
    try:
        author = next(search).fill()
        print("Working with the following Scholar profile: https://scholar.google.com/citations?user=" + author.id)
    except StopIteration:
        print("No author found with search term.")
        exit()

    check_hindex = calculate_hindex(author.publications)
    scopus_count, citation_comparisons, problematic_publications, missing_publications = comparisons("scopus.csv", author)

    write_citation_counts(author_name, citation_comparisons)
    write_missing_publications(author_name, missing_publications)
    # Output findings to console
    if check_hindex != author.hindex:
        print("The h-index we have calculated from the Google Scholar publications is not equal to the h-index publicly listed on their Scholar profile. Calculated - " + str(check_hindex) + ", Shown - " + str(author.hindex))
    print(str(len(author.publications)) + " publications were found for this Scholar on Google.")
    print(str(scopus_count) + " publications were found for this Scholar from the Scopus export.")
    print(str(scopus_count - len(missing_publications)) + " publications are common across both databases.")
    print(str(len(missing_publications)) + " publications on Scopus were not found on Scholar.")
    # Calculating the number of papers present on scholar but not scopus = Total scholar publications minus the common publications (total scopus count - not found on scholar)
    print(str(len(author.publications) - (scopus_count - len(missing_publications))) + " publications on Scholar were not found on Scopus.")
    print(str(len(problematic_publications)) + " publications on Scopus were not found on Scholar which may affect the h-index.")

    # Print our problematic publications to the console
    # Stored as [ [Title, Cite_Count] ]
    for miss in problematic_publications:
        pass
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

if __name__ == "__main__":
    main()

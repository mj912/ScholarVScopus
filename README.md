# ScholarVScopus

**About**

This python script is used to compare a list of publications exported from Scopus as a CSV format with a list of publications present on a Google Scholar profile. It notices that a publication may be titled slightly different across databases and uses a Levenshtein test to check whether the title is present. It determines the amount of publications that are present on one database and not the other. As Scholar indexes many more publications, it is expected that the Scopus database should be missing more publications then the Scholar database (i.e the Scholar database should contain more publications for an author). If any article is missing from the Google Scholar database and it is likely to affect the H-index, that is, it has more citations then the current listed H-index then the publications are printed to the console.

import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_dict = dict.fromkeys(corpus.keys(), 0.0)
    all_links = corpus[page]
    all_pages = set(corpus.keys())
    # If no links choose randomly from all pages
    if len(all_links) == 0:
        all_links = all_pages
    for p in all_links:
        prob_dict[p] += damping_factor / len(all_links)
    for p in all_pages:
        prob_dict[p] += (1-damping_factor) / len(all_pages)
    return prob_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages = list(corpus.keys())
    prob_dict = dict.fromkeys(corpus.keys(), 0.0)
    page = random.choice(all_pages)
    for i in range(n):
        prob_dict[page] += 1
        page = random.choices(population=all_pages, weights=list(transition_model(corpus, page, damping_factor).values()), k=1)[0]
    # Divide by N to calculate probability
    for p in all_pages:
        prob_dict[p] = prob_dict[p] / n
    return prob_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages = set(corpus.keys())
    n = len(all_pages)
    prob_dict = dict.fromkeys(corpus.keys(), 0.0)
    # Initialize rank to 1/N
    for p in all_pages:
        prob_dict[p] = 1 / n
    last_prob_dict = dict.fromkeys(corpus.keys(), 1.0)
    while max([abs(last - current) for last, current in zip(list(last_prob_dict.values()), list(prob_dict.values()))]) >= 0.001:
        last_prob_dict = prob_dict.copy()
        for page in all_pages:
            sum_for_page = 0
            for i in all_pages:
                all_links = corpus[i]
                # If a page has no links treat it as it has one link to every page
                if len(all_links) == 0:
                    all_links = all_pages
                # If page i has a link to current page add to sum
                if page in all_links:
                    sum_for_page += last_prob_dict[i] / len(all_links)
            prob_dict[page] = (1-damping_factor)/n + damping_factor*sum_for_page
    return prob_dict


if __name__ == "__main__":
    main()

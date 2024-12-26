from collections import defaultdict
import multiprocessing
import re


def map_function(document):
    word_counts = defaultdict(int)
    words = re.findall(r"\b\w+\b", document.lower())
    for word in words:
        word_counts[word] += 1
    return word_counts


def reduce_function(counts1, counts2):
    for word, count in counts2.items():
        counts1[word] += count
    return counts1


def map_reduce(documents):
    pool = multiprocessing.Pool()
    map_results = pool.map(map_function, documents)
    pool.close()
    pool.join()

    total_counts = defaultdict(int)
    for result in map_results:
        total_counts = reduce_function(total_counts, result)

    return total_counts


if __name__ == "__main__":
    with open("document.txt", "r") as file:
        documents = file.readlines()

    word_counts = map_reduce(documents)

    for word, count in word_counts.items():
        print(f"<{word}, {count}>")

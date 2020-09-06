#!/usr/bin/env python3

# Rube Codeberg competition entry for Pyconline2020
# Tim Bell - timothybell@gmail.com - @timb07

# The principle behind this entry is to produce the desired output
# using only freshly-downloaded characters from the internet, not
# characters contained in this script itself which might be stale
# or otherwise less than satisfactory.

import codecs
import hashlib
import random

from bs4 import BeautifulSoup
import requests

url = "https://2020.pycon.org.au/program/sun/"
exclamation_mark_url = "https://en.wikipedia.org/wiki/Exclamation_mark"

# Number of characters in the ngrams that will be assembled to
# create the desired output
NGRAM = 3

# Hashes of the trigrams we're looking for
hashes = [
    '148b21617e48c6f456634cba6e3d7bbafeb70fe58cc60202d957a97d5051e4d4',
    '16125286d427ff5bc259e9a610f655ed842751d305a248ed17d6bbdde188b32d',
    '52c40b80aad6933ae8e2ee36db00cc57685832d6f2fb364252278f84c11c3acd',
    '55e55555bda8f3c12c5e3519c4ebac8c954064df16b06bfc2dbcb97c75a7fde4',
    '87a10abd1154f862c4c43a32fb73ba4933a229a7e20398cb6bb2d7cc5ec5ca73',
    'b4d1e7ae27690a2232ed40d03b0ed208f6936d7e9fd89529075042a13fce7222',
    'b9206b99a1f8399d486330256d636b0002bd26a8272cde4714e44e679255450f',
    'c80c8d50188f8d00db226979d98bde5c181e1f152e7b63ef8329b82553d69b30',
    'd01fc93f9400615a84e4db6ef2a584f36bd9070c62d80d853b9ac9f1f102aa6f',
    'd0a407921672a57e599416f08ccf8e876c73b2a3486101ffe3a6af9acd8a9b9e',
]


def get_exclamation_mark(exclamation_mark_url):
    """
    Get an exclamation mark character from the given
    URL, which is assumed to be the Wikipedia entry
    for exclamation mark
    """
    r = requests.get(exclamation_mark_url)
    if r.status_code == 200:
        html_doc = r.text
    else:
        html_doc = ""
    soup = BeautifulSoup(html_doc, 'html.parser')
    return soup.table.th.text


def get_chars(url):
    """
    Get a range of characters from the provided URL,
    specifically alphanumeric characters, spaces and
    the exclamation mark.

    Note that the choice of the URL is important, since
    if it doesn't contain the characters we need the
    desired output string won't be completed.
    """
    exclamation_mark = get_exclamation_mark(exclamation_mark_url)
    r = requests.get(url)
    if r.status_code == 200:
        html_doc = r.text
    else:
        html_doc = ""
    soup = BeautifulSoup(html_doc, 'html.parser')
    text = soup.get_text()
    result = set()
    for c in text:
        if (c.isalpha() or c.isspace() or c == exclamation_mark) and c not in result:
            result.add(c)
    return "".join(result)


def candidate_combinations(chars):
    """
    Return random ngrams from the provided characters
    """
    while True:
        yield random.choices(chars, k=NGRAM)


def assemble_chars(chars, hashes):
    """
    Using the provided characters, assemble ngrams
    that match the provided hashes.
    """
    hash_set = {h for h in hashes}
    result = []
    for comb in candidate_combinations(chars):
        s = "".join(comb)
        h = hashlib.sha256(s.encode()).hexdigest()
        if h in hash_set:
            result.append(s)
            hash_set.remove(h)
            if not hash_set:
                break
    return result


def assemble_ngrams(ngrams):
    """
    Assemble the given ngrams into a complete string.
    The ngrams are assumed to overlap by NGRAM-1 characters.
    """
    result = ngrams[0]
    ngrams_remaining = ngrams[1:]
    while ngrams_remaining:
        ngrams_matched = []
        for ngram in ngrams_remaining:
            match = False
            if ngram[:NGRAM-1] == result[-(NGRAM-1):]:
                result += ngram[-1]
                match = True
            elif ngram[1:] == result[:NGRAM-1]:
                result = ngram[0] + result
                match = True
            if match:
                ngrams_matched.append(ngram)
        for ngram in ngrams_matched:
            ngrams_remaining.remove(ngram)
    return result


if __name__ == '__main__':
    # Get some fresh characters from the internet
    text = get_chars(url)
    # Form them into ngrams
    substrings = assemble_chars(text, hashes)
    # Assemble the ngrams
    s = assemble_ngrams(substrings)
    # Oh, did we mention that we were looking for the
    # rot13 encoding of the desired output?
    print(codecs.encode(s, 'rot_13'))

# -*- coding: utf-8 -*-
"""
scrape and clean sections from a page of poorly-structured HTML
"""

from bs4 import BeautifulSoup, NavigableString, Tag
import re


file_object = open('cleaned.html', 'r')
soup = BeautifulSoup(file_object, 'html.parser')
html = soup.contents[2]
body = html.body # html.find("body")

# wrapped in a <div>
# two <div>s in <body>
# [e.name for e in body.children]
# len(body.find_all('div'))  --> 193

# look for content strings that match date format
weekday = re.compile(r"(Mon|Tue|Tues|Wed|Wednes|Thu|Thur|Thurs|Fri)(day)?")
datestring = re.compile(r"^\s*(Mon|Tue|Tues|Wed|Wednes|Thu|Thur|Thurs|Fri|Sat|Satur|Sun)?(day)? [\d, ]+(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|July|Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December) 201\d\s*")
# [0-9, ]+
# (Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|July|Aug|August|Sep|Sept|September
# Oct|October|Nov|November|Dec|December)
# [0-9, ]+
# 201\d

# often wrapped in redundant <span>s
def get_parent_header(el):
    h2 = el.find_parent("h2")
    if not h2:
        while el.parent.name == "span":
            el = el.parent
        return el
    return h2

def extract_section(start_node, boundary_node):
    """ keep adding next sibling element until reaching boundary
    """
    group = []
    node = start_node
    
    # start at header node
    # and add siblings
    # until sibliing is boundary node or contains boundary node
    done = False
    while not done:
        if type(node) is NavigableString and not node == '\n':
            group.append(node)
        if type(node) is Tag:
            group.append(node)
        if node is not None:
            node = node.next_sibling
            done = node is boundary_node
        else:
            done = True
        # else:
            # not_done = node.find(string=boundary)
    return group

def extract_letters(chunk):
    #iterate lines/tags of chunk
    letters = []
    
    letter = soup.new_tag('article')
    for line in chunk:
        #until tag with text starting next letter
        # if text contains date regex
        # or id of letterN
        # and sibling line.find(text="/Letter \#\n+/")
        # catch TypeError
        try:
            if type(line) == NavigableString: 
                if re.match(datestring, line):
#                    print("matched string "+line)
                    letters.append(letter)
                    letter = soup.new_tag('article')
            # if multiple children, loop through and look for multiple matches
            # name is div, or other nested tags...
            # find_all is > 1
#            else:
            elif type(line) == Tag:
                datestrings = line.find_all(text=datestring)
                if (len(datestrings) > 1):
                    print("matched multiple in tag")
                    # multiple letters in unnecessary / poorly-placed enclosing tag
                    nested_letters = extract_letters(line)
                    letters.extend(nested_letters)
                elif (len(datestrings) > 0):
#                    print("matched single occurence tag")
                    letters.append(letter)
                    letter = soup.new_tag('article')
                    for span in line.find_all("span"):
                        span.unwrap()
        except TypeError as e:
#            print("Error: can't search in...")
#            print(type(line))
#            print(line)
            print(e)
        letter.append(line)

    letters.append(letter)
    return letters

def clean_html(chunk):
    cleaned = chunk
    # for tags in chunk
    # unwrap all font tags
    # unwrap span
    # find all the <span> and <font> and unwrap them
    return cleaned


def sib(node, count=1, collection=[]):
    collection.append(node)
    if (count == 1):
        return collection
    return sib(node.next_sibling, count - 1, collection)
        
    
# Letters are separated into groups of 10,
# introduced by <h2> elements containing "Letters X-X"
group_pattern = re.compile("^\s*Letters \d\d*\W?-\W?\d\d*\W?\s*$")

#body.find_all(string=datestring) # --> 377 matches
#for child in body.descendants:
section_breaks = body.find_all(string=group_pattern)

# sections = [node.find_parent("h2") for node in section_strings] #--> 59, including several None
# groups = map(get_parent_node, section_strings) --> map object
section_tags = [get_parent_header(break_el) for break_el in section_breaks]

# pass pairs of group headers to extract their section
sections = []
for n in range(len(section_tags)-2):
    start = section_tags[n]
    # ideally: skip the section header tag (<h2>Letters nn-nn</h2>)
    # and start with the next node, which should be the start of the letter
    end  = section_tags[n+1]
    sections.append( extract_section(start, end) )

# in each section, extract letters
#letters1 = extract_letters(sections[0])
letters_by_section = [extract_letters(section) for section in sections]
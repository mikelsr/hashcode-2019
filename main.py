#!/usr/bin/env python3

from itertools import chain
from sys import argv

from tsp_solver.greedy import solve_tsp

ENCODING = "ascii"
INPUT_FILES = [
    "data/a_example.txt",
    "data/b_lovely_landscapes.txt",
    "data/c_memorable_moments.txt",
    "data/d_pet_pictures.txt",
    "data/e_shiny_selfies.txt"
]
LIM = 1e7


"""
class Node:
    def __init__(self, slide):
        self.slide = slide
        self.paths = {}  # path: key=Node value=cost

    def __str__(self):
        return "{} {}".format(self.slide, ' '.join(["\n\tslide: {}\tcost: {}".format(x, y) for x, y in self.paths.items()]))
"""


# Pic only used for vertical photos
class Pic:
    def __init__(self, index, *args):
        self.index = index
        self.tags = set(args[2:])

    # merge combines two Pics into a Slide
    def merge(self, pic):
        intersection = common_tags(self.tags, pic.tags)
        tags = set(chain(self.tags, pic.tags - intersection))
        return Slide({self.index, pic.index}, tags)

    def __str__(self):
        return str(self.index)

    # verbose format for logging
    def __verbose__(self):
        return "{} {}".format(self.__str__(), ' '.join(self.tags))


# Slide is a single horizontal picture or two vertical ones merged
class Slide:
    def __init__(self, indices, tags):
        self.indices = indices
        self.tags = tags

    # format slide for output
    def __str__(self):
        return ' '.join([str(i) for i in self.indices])

    # verbose format for logging
    def __verbose__(self):
        return "{} {}".format(self.__str__(), ' '.join(self.tags))


"""
IN/OUT
"""


def input_from_file(filepath):
    with open(filepath, 'rb') as f:
        return f.read().decode(ENCODING)


def output_to_file(output, filepath):
    with open(filepath, 'wb') as f:
        f.write(output.encode(ENCODING))


def parse_input(raw):
    raw_pics = raw.strip().split('\n')

    # check number of photos
    if int(raw_pics[0]) != len(raw_pics) - 1:
        raise Exception("Expected ({}) and actual ({}) number of photos do not match".format(
            raw_pics[0], len(raw_pics) - 1
        ))

    h = []  # horizontal photos == slides
    v = []  # vertical photos
    i = 0
    for raw_pic in raw_pics[1:]:  # skip first element (n of photos)
        pic = raw_pic.split()
        if pic[0] == "H":
            h.append(Slide({i}, set(pic[2:])))
        else:
            v.append(Pic(i, *pic))
        i += 1
    return h, v


def parse_output(slides):
    return "{}\n{}".format(len(slides), ''.join(["{}\n".format(x) for x in slides]))


"""
UTILS
"""


# common_tags returns the intersection of two sets as a set
def common_tags(t1, t2):
    return t1.intersection(t2)


# score obtained concatenating two slides
def score(s1, s2):
    score_common = len(common_tags(s1.tags, s2.tags))
    score_s1 = len(s1.tags) - score_common
    score_s2 = len(s2.tags) - score_common
    return min(score_common, score_s1, score_s2)


"""
PROCESSING
"""


def pair_pics(pics):
    used = set()
    slides = set()
    i = 1
    for pic1 in pics:
        if len(used) == len(pics):
            break
        if pic1 in used:
            continue

        common = len(pic1.tags)  # maximum possible tags in common
        pic = None  # pic2 will be the Pic paired with pic1
        j = 0
        for pic2 in pics[i:]:
            if pic2 in used:
                continue
            if j > LIM:
                break
            c = len(common_tags(pic1.tags, pic2.tags))
            if c < common:
                common = c
                pic = pic2
            j += 1
        if pic is None:
            raise Exception("Chosen picture is 'None'")
        used.update({pic1, pic})
        slides.update({pic1.merge(pic)})

    return slides


"""
def create_graph(slides):
    sorted_slides = sorted(list(slides), key=lambda x: len(x.tags))
    nodes = []
    for s1 in sorted_slides:
        candidates = []
        best_score = 0
        for s2 in sorted_slides:
            if s1 is s2:
                continue
            current_score = score(s1, s2)
            if current_score > best_score:
                candidates = [s2]
                best_score = current_score
            elif current_score == best_score:
                candidates.append(s2)
        n = Node(s1)
        cost = 1/((best_score+1) if best_score != 0 else 1)
        for c in candidates:
            n.paths[c] = cost
        nodes.append(n)
    return nodes
"""


def create_graph(slides):
    ordered_slides = list(slides)
    matrix = []
    for s1 in ordered_slides:
        row = []
        for s2 in ordered_slides:
            # cost between the same node = 0
            if s1 is s2:
                row.append(0)
                continue
            s = score(s1, s2)
            row.append(1/s if s != 0 else 1.0)  # default cost is 1 (max)
        matrix.append(row)
    return matrix, ordered_slides


def print_matrix(matrix, ordered_slides):
    print("\t{}".format('\t'.join(["({})".format(s) for s in ordered_slides])))
    for i in range(len(ordered_slides)):
        print("({})\t{}".format(ordered_slides[i], '\t'.join(str(c) for c in matrix[i])))


"""
MAIN
"""


def main(n=0, out_dir="out"):
    raw = input_from_file(INPUT_FILES[n])
    h, v = parse_input(raw)

    v_slides = pair_pics(v)

    slides = set(h)
    slides.update(v_slides)
    if len(slides) != len(h) + len(v)//2:
        raise Exception("Total ({}), horizontal({}) and vertical/2 ({}) do not match".format(
            len(slides), len(h), len(v)//2
        ))
    # print("slides combined")

    matrix, ordered = create_graph(slides)
    order = solve_tsp(matrix)
    final = [ordered[i] for i in order]


    # write output to file
    out = parse_output(final)
    output_to_file(out, "{}/{}.out".format(out_dir, n))


if __name__ == "__main__":
    n = 3
    out_dir="out"
    if len(argv) > 1:
        n = int(argv[1])
    if len(argv) > 2:
        out_dir = argv[2]
    main(n, out_dir)


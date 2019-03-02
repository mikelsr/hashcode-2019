#!/usr/bin/env python3

from itertools import chain
from sys import argv

ENCODING = "ascii"
INPUT_FILES = [
    "data/a_example.txt",
    "data/b_lovely_landscapes.txt",
    "data/c_memorable_moments.txt",
    "data/d_pet_pictures.txt",
    "data/e_shiny_selfies.txt"
]
LIM = 1e7


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


def sort_slides(slides):
    sorted_slides = sorted(list(slides), key=lambda x: len(x.tags))

    ordered = [sorted_slides[0]]
    used = {sorted_slides[0]}

    total = len(slides)
    i = 0
    while len(used) != total:
        slide1 = ordered[i]
        # print(slide1)
        points = -1
        slide = None
        j = 0
        for slide2 in sorted_slides:
            if slide2 in used:
                continue
            if j > LIM:
                break
            p = score(slide1, slide2)
            if p > points:
                points = p
                slide = slide2
            j += 1
        if slide is None:
            raise Exception("Chosen exception is 'None'")
        used.update({slide})
        ordered.append(slide)
        i += 1
    # print(ordered[-1])
    return ordered


"""
MAIN
"""


def main(n=0, out_dir="out"):
    raw = input_from_file(INPUT_FILES[n])
    h, v = parse_input(raw)
    # print("input parsed")
    # print("\n* Horizontals:")
    # for x in h:
    #     print(x.__verbose__())
    # print("\n* Verticals:")
    # for x in v:
    #     print(x.__verbose__())

    v_slides = pair_pics(v)
    # print("vertical pictures paired")
    # print("\n*Vertical slides:")
    # for s in v_slides:
    #     print(s.__verbose__())

    slides = set(h)
    slides.update(v_slides)
    if len(slides) != len(h) + len(v)//2:
        raise Exception("Total ({}), horizontal({}) and vertical/2 ({}) do not match".format(
            len(slides), len(h), len(v)//2
        ))
    # print("slides combined")

    # write output to file
    slides = sort_slides(slides)
    out = parse_output(slides)
    output_to_file(out, "{}/{}.out".format(out_dir, n))


if __name__ == "__main__":
    n = 0
    out_dir="out"
    if len(argv) > 1:
        n = int(argv[1])
    if len(argv) > 2:
        out_dir = argv[2]
    main(n, out_dir)

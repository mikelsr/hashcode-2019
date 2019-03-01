#!/usr/bin/env python3

from itertools import chain

ENCODING = "ascii"
INPUT_FILES = [
    "data/a_example.txt",
    "data/b_lovely_landscapes.txt",
    "data/c_memorable_moments.txt",
    "data/d_pet_pictures.txt",
    "data/e_shiny_selfies.txt"
]


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
            h.append(Slide({i}, pic[2:]))
        else:
            v.append(Pic(i, *pic))
        i += 1
    return h, v


def parse_output(pics):
    return ''.join(["{}\n".format(x) for x in pics])


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
        for pic2 in pics[i:]:
            if pic2 in used:
                continue
            c = len(common_tags(pic1.tags, pic2.tags))
            if c < common:
                common = c
                pic = pic2
        if pic is None:
            raise Exception("Chosen picture is 'None'")
        used.update({pic1, pic})
        slides.update({pic1.merge(pic)})

    return slides


# TODO
def sort_slides(slides):
    pass


"""
MAIN
"""


def main():
    raw = input_from_file(INPUT_FILES[2])
    h, v = parse_input(raw)
    print("\n* Horizontals:")
    for x in h:
        print(x.__verbose__())
    print("\n* Verticals:")
    for x in v:
        print(x.__verbose__())

    v_slides = pair_pics(v)
    print("\n*Vertical slides:")
    for s in v_slides:
        print(s.__verbose__())


if __name__ == "__main__":
    main()

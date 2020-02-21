####################################################################
# Original is here: https://github.com/DecentGradient/hashcode2019 #
####################################################################

import copy


class photo():
    def __init__(self, string, pid):
        elements = string.split()
        self.pos = elements[0]
        self.tags = set(elements[2:])
        self.pid = str(pid)

    def get_len(self):
        return len(self.tags)

    def intersection(self, photo):
        return len(self.tags.intersection(photo.tags))

    def difference(self, photo):
        return len(self.tags.difference(photo.tags))

    def get_lunion(self, photo):
        return len(self.tags & photo.tags)

    def get_score(self, photo):
        return min(self.intersection(photo),
                   self.difference(photo),
                   photo.difference(self))

    def merge(self, photo):
        self.add_tags(photo.tags)
        if photo.pid != self.pid:
            self.pid = "{} {}".format(self.pid, photo.pid)

    def add_tags(self, tags_):
        self.tags = self.tags & tags_


def get_largest(photos):
    photos["H"] = sorted(photos["H"],
                         key=lambda x: x.get_len(),
                         reverse=True)
    ## get the largest V
    photos["V"] = sorted(photos["V"],
                         key=lambda x: x.get_len(),
                         reverse=True)
    lvi = 0
    mvt = len(photos["V"][0].tags)
    for i, pv in enumerate(photos["V"]):
        if photos["V"][0].get_lunion(pv) > mvt:
            mvt = photos["V"][0].get_lunion(pv)
            lvi = i
    if mvt > len(photos["H"][0].tags):
        # remove V
        new_V = photos["V"][0]
        new_V.merge(photos["V"][lvi])
        photos["V"] = photos["V"][1:lvi] + photos["V"][lvi + 1:]
        return new_V, photos
    else:
        new_H = photos["H"][0]
        photos["H"] = photos["H"][1:]
        return new_H, photos


def get_best_match(sim, photos):
    # Get best match given vertical and horizontal
    # images
    max_h_score = 0
    if len(photos["H"]) > 0:
        hid, new_H = max(enumerate(photos["H"]),
                         key=lambda x: sim.get_score(x[1]))
        max_h_score = sim.get_score(new_H)
    if len(photos["V"]) > 0:
        sortedV = sorted(copy.deepcopy(photos["V"]),
                         key=lambda x: sim.difference(x),
                         reverse=True)
        new_V = sortedV[0]
        new_V.merge(sortedV[-1])
        print(sim.pid, "----", new_V.pid, "-----", new_V.get_score(sim), max_h_score)
        if new_V.get_score(sim) >= max_h_score:
            photos["V"] = sortedV[1:-1]
            return sim.get_score(new_V), new_V, photos
    # else return H
    photos["H"] = photos["H"][:hid] + photos["H"][hid + 1:]
    display_photos(photos)
    return sim.get_score(new_H), new_H, photos


def display_photos(photos):
    print("H: {}, V: {}".format([x.pid for x in photos["H"]],
                                [x.pid for x in photos["V"]]))


def display_slideshow___(slideshow):
    print([x.pid for x in slideshow])


def generate_slideshow(first_img, photos):
    slideshow = [first_img]
    while len(photos["H"]) > 0 or len(photos["V"]) > 0:
        left_side = get_best_match(slideshow[0], copy.deepcopy(photos))
        right_side = get_best_match(slideshow[-1], copy.deepcopy(photos))
        if left_side[0] > right_side[0]:
            slideshow = [left_side[1]] + slideshow
            photos = left_side[2]
            display_photos(photos)
        else:
            slideshow = slideshow + [right_side[1]]
            photos = right_side[2]
            display_photos(photos)
    return slideshow


def read_data(fname):
    V_photos = []
    H_photos = []
    with open(fname) as f:
        n = int(f.readline()[:-1])
        data = f.readlines()
        pid = 0
        for line in data:
            if (line[0] == 'H'):
                H_photos.append(photo(line[:-1], pid))
            else:
                V_photos.append(photo(line[:-1], pid))
            pid += 1
    return {"H": H_photos, "V": V_photos}


def display_slideshow(slideshow):
    print(len(slideshow))
    for s in slideshow:
        print(s.pid)


display_slideshow(generate_slideshow(*get_largest(read_data("a_example.txt"))))
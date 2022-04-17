# If programming the algorithm from scratch is too difficult, you can use this skeleton.
# I tried to keep it as simple as positionsible; as a consequence degenerate cases will not be handled and the algorithm is not robust.
# As data structues for the Event queue and for the status, it uses SortedList.
# I have left some TODOs with question marks for you to fill in. Search for TODOs and add code there, according to what you have learned in the videos.

from sortedcontainers import SortedList
from fractions import Fraction
from functools import total_ordering

import numpy as np
import pylab as pl
from matplotlib import collections  as mc


class Segment:
    def __init__(self, x1, y1, x2, y2, current_y_list=None):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.current_y_list = current_y_list  # stored in list to have it mutable

        if y1 == y2:
            raise Exception('Horizontal segments not supported.')
        if x1 == x2:
            raise Exception('Vertical segments not supported.')
        else:
            self.slope = (y2 - y1) / (x2 - x1)
            self.intersept = y2 - self.slope * x2

    def current_x(self):
        return (self.current_y_list[0] - self.intersept) / self.slope

    # TODO: when inserting into the status we need a comparison operator between segments.
    # I.e. we need to implement "<" (that is __lt__) and "==" (that is __eq__).
    # What attribute(s) or method(s) do we need to call?
    # Below I filled in x1 (self.x1 < other.x1; self.x1 == other.x1), but that is certainly wrong
    # Change these two lines to make the comparison work correctly
    def __lt__(self, other):
        return self.current_x() < other.current_x()

    def __eq__(self, other):
        return (self.current_x() - other.current_x()) < 1e-4

    def intersection(self, other):
        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2
        xA = other.x1
        yA = other.y1
        xB = other.x2
        yB = other.y2

        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = xB - xA
        dy2 = yB - yA
        determinant = (-dx1 * dy2 + dy1 * dx2)

        # if math.fabs(determinant) < DET_TOLERANCE: raise Exception('...')
        if determinant == 0:
            raise Exception('Intersection implementation not sufficiently robust for this input_data.')
        det_inv = Fraction(1, determinant)

        r = Fraction((-dy2 * (xA - x1) + dx2 * (yA - y1)), determinant)
        s = Fraction((-dy1 * (xA - x1) + dx1 * (yA - y1)), determinant)

        if r < 0 or r > 1 or s < 0 or s > 1:
            return None

        # return the average of the two descriptions
        xi = x1 + r * dx1
        yi = y1 + r * dy1
        return xi, yi


class Event:
    class Type:
        INTERSECTION = 0
        START = 1
        END = 2

    def __init__(self, type, segment, segment2=None, intersection_point=None):
        self.type = type
        self.segment = segment
        # segment2 = None for non-intersection events
        self.segment2 = segment2

        if type == 1:
            if segment.y1 < segment.y2 or (segment.y1 == segment.y2 and segment.x2 < segment.x1):
                self.key = (segment.y2, -segment.x2)
            else:
                self.key = (segment.y1, -segment.x1)

        elif type == 2:
            if segment.y1 > segment.y2 or (segment.y1 == segment.y2 and segment.x2 > segment.x1):
                self.key = (segment.y2, -segment.x2)
            else:
                self.key = (segment.y1, -segment.x1)

        elif type == 0:
            # compute intersection point
            # self.key = (segment.intersection(segment2)[1], -segment.intersection(segment2)[0])
            self.key = (intersection_point[1], -intersection_point[0])


def check_intersection(position, position2, events, status):
    segment1 = status[position]
    segment2 = status[position2]
    intersection_point = segment1.intersection(segment2)

    if intersection_point and intersection_point[1] < segment1.current_y_list[0]:
        intersection_event = Event(0, segment1, segment2, intersection_point)
        index = events.bisect_left(intersection_event)
        # for simplicity we assume general position:
        if index == len(events) or not events[index].key == (intersection_point[1], -intersection_point[0]):
            events.add(intersection_event)


def handle_start_event(segment, events, status):
    # print("Inserting", segment.x1, segment.y1, segment.x2, segment.y2)
    status.add(segment)

    position = status.index(segment)
    if position > 0:
        check_intersection(position - 1, position, events, status)
    if position + 2 < len(status):
        check_intersection(position, position + 1, events, status)
    # If you don't know where to start, you can look at the event handling for intersection events
    # print("Code is missing here.")


def handle_end_event(segment, events, status):
    # print("Removing", segment.x1, segment.y1, segment.x2, segment.y2)
    position = status.index(segment)
    if 0 < position < len(status)-1:
        check_intersection(position - 1, position + 1, events, status)

    status.remove(segment)
    # If you don't know where to start, you can look at the event handling for intersection events
    # print("Code is missing here.")


def handle_intersection_event(segment, segment2, events, status):
    current_y = segment.current_y_list[0]
    segment.current_y_list[
        0] = current_y + 0.00001  # we need to make sure that the comparison operator is consistent with the order just before the event

    # print("Handling intersection", segment.x1, segment.y1, segment.x2, segment.y2, segment2.x1, segment2.y1, segment2.x2, segment2.y2)

    ## swapping is not implemented for SortedList, so we need a trick here
    position1 = status.index(segment)
    position2 = status.index(segment2)
    # status[position1] = segment2
    # status[position2] = segment
    ## instead we can remove and reinsert one of the segments.
    status.remove(segment)
    segment.current_y_list[0] = current_y - 0.00001
    status.add(segment)

    position_first = min(position1, position2)

    if position_first > 0:
        check_intersection(position_first - 1, position_first, events, status)
    if position_first + 2 < len(status):
        check_intersection(position_first + 1, position_first + 2, events, status)

    segment.current_y_list[0] = current_y


def write_type_event_to_file(filename, data):
    f = open(f"output_files/{filename}.txt", "w")
    f.write(str(data))
    f.close()


def sweep(input_segments):
    endpoint_events = []
    for s in input_segments:
        endpoint_events.append(Event(1, s))
        endpoint_events.append(Event(2, s))

    events = SortedList(endpoint_events, key=lambda x: x.key)
    status = SortedList()
    # status = SortedList(key=segment.current_x) This wouldn't work since keys are cached

    number_of_events = 0
    number_of_intersections = 0

    current_y_list = input_segments[0].current_y_list
    lines = []

    while events:
        e = events.pop()
        number_of_events += 1
        current_y_list[0] = e.key[0]

        if e.type == 1:
            handle_start_event(e.segment, events, status)
            lines.append([[e.segment.x1, e.segment.y1], [e.segment.x2, e.segment.y2]])

        elif e.type == 2:
            handle_end_event(e.segment, events, status)
            lines.remove([[e.segment.x1, e.segment.y1], [e.segment.x2, e.segment.y2]])

        else:
            number_of_intersections += 1
            handle_intersection_event(e.segment, e.segment2, events, status)

        if number_of_events in [3, 17, 99]:
            write_type_event_to_file(f"event_type_{number_of_events}", e.type)
            print("Event", number_of_events, ":", e.type)

        ## Can be useful for debugging
        # print("status:")
        # for s in status:
        #     print(s.x1, s.y1, s.x2, s.y2, s.current_x())
        #     lc = mc.LineCollection(lines, linewidths=2)
        #     fig, ax = pl.subplots()
        #     ax.add_collection(lc)
        #     ax.autoscale()
        #     ax.margins(0.1)
        #     pl.show()

    write_type_event_to_file("nr_of_intersections", number_of_intersections)
    print("Number of intersections:", number_of_intersections)

    write_type_event_to_file("nr_of_events", number_of_events)
    print("Number of events:", number_of_events)


def readsegments(file):
    current_y_list = [0]
    segments = []
    with open(file) as f:
        for line in f:
            coordinates = [int(x) for x in line.split()]
            s = Segment(coordinates[0], coordinates[1], coordinates[2], coordinates[3], current_y_list)
            segments.append(s)

    return segments


if __name__ == "__main__":
    input_data = readsegments("input_files/Linesegments2.txt")
    sweep(input_data)

__version__ = "1.0.0"

WINDOW_SIZE = 3
WINDOW_PCT = 0.05
SPACER = 700


def collapse(a):
    bin_edges = []
    try:
        # bin array is already sorted.
        bins = a[0:1]
        for each in a[1:]:
            # calculate threshold
            dv = max(WINDOW_SIZE, WINDOW_PCT * bins[0])
            if (each - bins[0]) > dv:
                # close current bin collection
                bin_edges.append(bins)
                # setup for new bin collection
                bins = []
            # collapse it in
            bins.append(each)

        # last bin collection.
        bin_edges.append(bins)
        return bin_edges

    except Exception, e:
        print "ERR:collapse: %s" % e
        return None


class IRHistogram:
    def __init__(self, a):
        try:
            self.bins = list(set(a))
            self.bins.sort()
            self.bin_edge = collapse(self.bins)

        except Exception, e:
            print "ERR:IRHistogram:__init__: %s" % e


class BurstPairs:
    def __init__(self, a):
        try:
            self.array = a
            self.pulses = IRHistogram(self.array[0::2])
            self.gaps = IRHistogram(self.array[1::2])
            self.pixels = self.pixelate()
            self.main_frame, self.repeat_frame, self.repeat_count, self.code_type = self.dissect()
            self.report()

        except Exception, e:
            print "ERR:BurstPairs:__init__: %s" % e

    def report(self):
        print self.code_type

    def pixelate(self):
        a = [None] * len(self.array)
        try:
            # pulses
            for x in xrange(0, len(self.array), 2):
                for y in xrange(len(self.pulses.bin_edge)):
                    if self.array[x] in self.pulses.bin_edge[y]:
                        a[x] = y
            # gaps
            for x in xrange(1, len(self.array), 2):
                for y in xrange(len(self.gaps.bin_edge)):
                    if self.array[x] in self.gaps.bin_edge[y]:
                        a[x] = y
            return a

        except Exception, e:
            print "ERR:BurstPairs:pixelate: %s" % e
            return None

    ## compare 2 frames for
    #   None - different, no frame returned.
    #   a frame - identical, return the complete one.
    #
    def frame_compare(self, frame1, frame2):
        try:
            size1 = frame1[1] - frame1[0]
            size2 = frame2[1] - frame2[0]
            if size1 > size2:
                # possibly a repeat frame
                return None
            # do not compare lead-in pulse and lead-out gap
            for x in xrange(size1 - 2):
                if self.pixels[frame1[1]-1-x] != self.pixels[frame2[1]-1-x]:
                    return None
            if size1 == size2:
                return frame1
            else:
                return frame2

        except Exception, e:
            print "ERR:BurstPairs:pixelate: %s" % e
            return None

    ## cut into frames.  frame separation rely on logic of lead-in and lead-out.
    def dissect(self):
        try:
            frame_edges = [-1]  # mark for where 1st frame started.
            th = min(SPACER, self.gaps.bins[-1])  # lead-out gap.
            # mark all the end of frames by looking for lead-out gap.
            for x in xrange(1, len(self.array), 2):
                if self.array[x] > th:
                    frame_edges.append(x)
                # only frame with lead-out is usable, do not add the remains.

            # no frame.
            if len(frame_edges) < 2:
                return None, None, 0, 'Fail'

            main_frame = [frame_edges[0], frame_edges[1]]
            repeat_frame = []
            repeat_count = 1

            # look for main frame.
            for x in xrange(2, len(frame_edges)):
                repeat_frame = [frame_edges[x-1], frame_edges[x]]
                frame = self.frame_compare(main_frame, repeat_frame)
                if frame is None:
                    break
                main_frame = frame
                repeat_count += 1

            # full repeat main frames.
            if repeat_count >= (len(frame_edges) - 1):
                return main_frame, None, repeat_count, 'Full_Repeat'

            # look for repeat frame.
            for x in xrange(2+repeat_count, len(frame_edges)):
                frame = self.frame_compare(repeat_frame, [frame_edges[x-1], frame_edges[x]])
                if frame is None:
                    # [TBD] what now?
                    break
                repeat_frame = frame
                repeat_count += 1

            return main_frame, repeat_frame, repeat_count, 'Partial_Repeat'

        except Exception, e:
            print "ERR:BurstPairs:dissect: %s" % e
            return None, None, 0, 'Fail'
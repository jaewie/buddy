CHUNK_SIZE = 64
LEVELS = 4
MAX_SIZE = CHUNK_SIZE * 2 ** LEVELS


class OutOfMemory(Exception):
    pass


class MemoryAllocator:
    def __init__(self):
        self.chunks = [set() for _ in range(LEVELS)]
        self.chunks[-1].add(0)
        self.boundaries = {}

    def allocate(self, size):
        target_level = size // CHUNK_SIZE

        curr_level = next(
            (i for i in range(target_level, len(self.chunks)) if self.chunks[i]), None
        )
        if curr_level is None:
            raise OutOfMemory("No more space to allocate {}".format(size))

        # Do chunk breaks
        while curr_level > target_level:
            chunk_location = self.chunks[curr_level].pop()
            chunk_size = CHUNK_SIZE * 2 ** curr_level

            self.chunks[curr_level - 1].add(chunk_location)
            self.chunks[curr_level - 1].add(chunk_location + chunk_size // 2)
            curr_level -= 1

        ans = self.chunks[target_level].pop()
        self.boundaries[ans] = target_level
        return ans

    def free(self, chunk_location):
        curr_level = self.boundaries[chunk_location]
        del self.boundaries[chunk_location]

        chunk_size = CHUNK_SIZE * 2 ** curr_level
        buddy = find_buddy(chunk_location, chunk_size, MAX_SIZE)

        # Modify curr_level, chunk_location until we can't coalesce anymore
        while buddy in self.chunks[curr_level]:
            self.chunks[curr_level].remove(buddy)

            chunk_location = min(chunk_location, buddy)
            curr_level += 1
            chunk_size = CHUNK_SIZE * 2 ** curr_level
            buddy = find_buddy(chunk_location, chunk_size, MAX_SIZE)

        self.chunks[curr_level].add(chunk_location)


def find_buddy(chunk_location, chunk_size, max_size):
    lo = -max_size
    hi = max_size

    while lo <= hi:
        mid = lo + (hi - lo) // 2

        if mid == chunk_location:
            if mid + chunk_size == hi:
                return mid - chunk_size
            return mid + chunk_size

        if chunk_location > mid:
            lo = mid
        else:
            hi = mid
    assert False

class Timer(object):

    def __init__(self, max_time, max_count=1):
        self.time = 0
        self.count = 0
        self.MAX_TIME = max_time*1000
        self.MAX_COUNT = max_count
        self.time_limit_hit = False
        self.count_limit_hit = False

    def update(self, time_passed):
        self.time += time_passed
        if (self.time >= self.MAX_TIME
            and self.MAX_TIME > 0):
            self.max_time_trigger()

    def reset(self):
        self.time = 0
        self.count = 0
        self.time_limit_hit = False
        self.count_limit_hit = False

    def max_time_trigger(self):
        self.time -= self.MAX_TIME
        self.count += 1
        self.time_limit_hit = True
        if self.count >= self.MAX_COUNT:
            self.max_count_trigger()

    def max_count_trigger(self):
        self.count_limit_hit = True


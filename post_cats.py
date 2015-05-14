import redis
import sys
import gzip
import time
import argparse


class Timer(object):
    def __init__(self):
        self.start_time = time.time()
        self.last_time = self.start_time
        self.end_time = None

    def mark(self, fmt, *argv):
        cur_time = time.time()
        print cur_time-self.last_time, fmt % argv
        self.last_time = cur_time

    def end(self):
        if self.end_time is None:
            self.end_time = time.time()
        return self.end_time - self.start_time


class MyRedis(object):
    def __init__(self, host, port, db, flush_count, upload_script_fn):
        self.r = redis.StrictRedis(host=host, port=port, db=db)
        self.flush_count = flush_count
        script_lines = [_ for _ in open(upload_script_fn)]
        self.sha = self.r.script_load('\n'.join(script_lines))

    def add_entries(self, reader, start_uid=None):
        timer = Timer()
        r_pipe, lines, num_flushes = None, 0, 0
        okay = True if start_uid is None else False
        for uid, tuples in (_.strip().split(None, 1) for _ in reader):
            uid = int(uid)
            if not okay:
                if uid == start_uid:
                    okay = True
                else:
                    continue
            if r_pipe is None:
                r_pipe = self.r.pipeline()
            r_pipe.evalsha(self.sha, 1, uid, tuples)
            lines += 1
            if lines % 100 == 0:
                r_pipe.execute()
                r_pipe = None
                num_flushes += 1
            if lines % 10000 == 0:
                timer.mark('inserted: %d, flushes: %d', lines, num_flushes)
        if r_pipe is not None:
            r_pipe.execute()
            num_flushes += 1
        total_time = timer.end()
        print total_time, 'inserted: %d, flushes: %d' % (lines, num_flushes)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=6379, type=int)
    parser.add_argument('--db', default=0, type=int)
    parser.add_argument('--flush', default=100, type=int)
    parser.add_argument('--upload_script', default='bf.lua')
    parser.add_argument('--start_uid', type=int)
    parser.add_argument('files', nargs='*')
    pa = parser.parse_args()
    my_redis = MyRedis(pa.host, pa.port, pa.db, pa.flush, pa.upload_script)
    for fn in pa.files:
        reader = gzip.open(fn) if fn.endswith('.gz') else open(fn)
        my_redis.add_entries(reader, pa.start_uid)


if __name__ == '__main__':
    main()

from rq import Queue, Worker, Connection
if '' not in sys.path:
    sys.path.insert(0, '')


if __name__ == '__main__':
    # Tell rq what Redis connection to use
    with Connection():
        q = Queue()
        Worker(q).work()

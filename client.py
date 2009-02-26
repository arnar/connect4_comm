from SimpleXMLRPCServer import SimpleXMLRPCServer
import pexpect

import time

def log(str):
    print time.strftime("[%Y-%m-%dt%H:%M:%S]"), str

class Player(object):

    def __init__(self, exe):
        log('Initializing player...')
        self.p = pexpect.spawn(exe)
        self.p.expect("> ")
        self.reset()
        log('...done')

    def _cmd(self, cmd):
        self.p.sendline(cmd)
        self.p.expect("> ")

    def get_state(self):
        log("Getting state...")
        self._cmd("p")
        st = self.p.before.strip().split()[-1]
        log("...done -> " + st)
        return st
    
    state = property(get_state)

    def move(self, move):
        log("Performing move: " + move)
        self._cmd("m " + move)
        return self.get_state()

    def go(self):
        log("Searching (depth=%d)..." % self.depth)
        t0 = time.time()
        self._cmd("g")
        t = time.time() - t0
        log("Search finished in %.2f seconds" % t)
        lines = self.p.before.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("bestmove "):
                log("Found move: " + line)
                return (line.split()[1], t, self.get_state())
        raise Exception("Player did not give bestmove.")

    def retract(self):
        log("Retracting")
        self._cmd("r")
        return self.get_state()

    def reset(self):
        log("Resetting")
        self._cmd("i")
        self.depth = 4
        return self.get_state()

    def get_depth(self):
        return self._depth

    def set_depth(self, depth):
        log("Setting depth to %d" % depth)
        self._depth = depth
        self._cmd("d %d" % depth)
        return self._depth

    def increase_depth(self):
        return self.set_depth(self._depth + 1)

    def decrease_depth(self):
        if self._depth > 0:
            return self.set_depth(self._depth - 1)
        else:
            return self._depth

    depth = property(get_depth, set_depth)

    def terminate(self):
        log("Terminating player")
        self._cmd("q")
        return 0

def main(player_exe):
    p = Player(player_exe)
    server = SimpleXMLRPCServer(("", 8000))
    server.register_instance(p)
    server.serve_forever()

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))

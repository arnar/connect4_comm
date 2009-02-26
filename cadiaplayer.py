from SimpleXMLRPCServer import SimpleXMLRPCServer
import subprocess
import os

import time

def log(str):
    print time.strftime("[%Y-%m-%dt%H:%M:%S]"), str

# Note that:
#  Our system     Cadia player
#    BLACK          WHITE
#    RED            BLACK

class GGPlayer(object):
    
    def __init__(self, exe, role, game, start, play):
        self.role = role
        self.p = subprocess.Popen(exe, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 cwd=os.path.dirname(exe))
        status = self._cmd("(start id %s (%s) %d %d)" % (self.role, game, start, play))
        assert status == "READY"

    def _cmd(self, cmd):
        log("PIPE: sending %r" % cmd)
        self.p.stdin.write(cmd + "\r\n")
        ret = self.p.stdout.readline()
        log("PIPE: got %r" % ret)
        return ret.strip()

    def play(self, moves=None):
        if moves is None:
            mv = self._cmd("(play id nil)")
        else:
            mv = self._cmd("(play id (%s))" % ' '.join(moves))
        return mv
    
    def stop(self, moves):
        mv = self._cmd("(stop id (%s))" % ' '.join(moves))
        return mv

    def state(self):
        log("PIPE: sending '(state)'")
        self.p.stdin.write("(state)\r\n")
        ret = [self.p.stdout.readline().strip() for i in range(43)]
        log("PIPE: read 43 lines of state")
        return ret

class Player(object):

    def __init__(self, exe, role):
        log('Initializing player...')
        self.last_opponent_move = None
        self.gp = GGPlayer(exe, role, THEGAME, 5, 5)
        log('...done')

    def get_state(self):
        log("Getting state...")
        st = self.gp.state()
        log("...done -> " + st)
        return repr(st)
    
    state = property(get_state)

    def move(self, move):
        log("Registering move: " + move)
        self.last_opponent_move = "(drop %d)" % " abcdefg".find(move)
        return "cadiaplayer"

    def go(self):
        log("Searching...")
        if self.last_opponent_move is not None:
            if self.gp.role == 'white':
                mvs = ["noop", self.last_opponent_move]
            else:
                mvs = [self.last_opponent_move, "noop"]
        else:
            mvs = None
        t0 = time.time()
        mv = self.gp.play(mvs)
        t = time.time() - t0
        log("Search finished in %.2f seconds" % t)
        assert mv.startswith("(drop ")
        themove = "abcdefg"[int(mv[1:-1].split()[1])]
        log("Found move: " + themove)
        log("Making the move on cadiaplayer side...")
        if self.gp.role == 'white':
            mvs = [mv, "noop"]
        else:
            mvs = ["noop", mv]
        nopmove = self.gp.play(mvs)
        assert nopmove == "noop"
        return (themove, t, self.get_state())

    def retract(self):
        raise Exception("cannot retract cadiaplayer")

    def reset(self):
        raise Exception("cannot reset cadiaplayer")

    def get_depth(self):
        return 0

    def set_depth(self, depth):
        return 0

    def increase_depth(self):
        return 0

    def decrease_depth(self):
        return 0

    depth = property(get_depth, set_depth)

    def terminate(self):
        return 0

def main(exe, role):
    p = Player(exe, role)
    server = SimpleXMLRPCServer(("", 8000))
    server.register_instance(p)
    server.serve_forever()

THEGAME = """(role white) 
(role black) 


(init (cell 1 1 b))
(init (cell 1 2 b))
(init (cell 1 3 b))
(init (cell 1 4 b))
(init (cell 1 5 b))
(init (cell 1 6 b))
(init (cell 2 1 b))
(init (cell 2 2 b))
(init (cell 2 3 b))
(init (cell 2 4 b))
(init (cell 2 5 b))
(init (cell 2 6 b))
(init (cell 3 1 b))
(init (cell 3 2 b))
(init (cell 3 3 b))
(init (cell 3 4 b))
(init (cell 3 5 b))
(init (cell 3 6 b))
(init (cell 4 1 b))
(init (cell 4 2 b))
(init (cell 4 3 b))
(init (cell 4 4 b))
(init (cell 4 5 b))
(init (cell 4 6 b))
(init (cell 5 1 b))
(init (cell 5 2 b))
(init (cell 5 3 b))
(init (cell 5 4 b))
(init (cell 5 5 b))
(init (cell 5 6 b))
(init (cell 6 1 b))
(init (cell 6 2 b))
(init (cell 6 3 b))
(init (cell 6 4 b))
(init (cell 6 5 b))
(init (cell 6 6 b))
(init (cell 7 1 b))
(init (cell 7 2 b))
(init (cell 7 3 b))
(init (cell 7 4 b))
(init (cell 7 5 b))
(init (cell 7 6 b))


(init (control white))


(succ 1 2)
(succ 2 3)
(succ 3 4)
(succ 4 5)
(succ 5 6)
(succ 6 7)


(<= (cm ?c ?r)
    (or (true (cell ?c ?r x))
        (true (cell ?c ?r o))))


(<= (sequential ?a ?b ?c ?d)
    (succ ?a ?b)
    (succ ?b ?c)
    (succ ?c ?d))


(<= (top-unused ?c ?r)
    (true (cell ?c ?r b))
    (cm ?c ?s)
    (succ ?s ?r))
    
(<= (top-unused ?c 1)
        (true (cell ?c 1 b)))


(<= (plays-on ?c ?r)
    (does ?x (drop ?c))
    (top-unused ?c ?r))


(<= (next (cell ?c ?r ?x))
    (true (cell ?c ?r ?x))
    (not (plays-on ?c ?r)))


(<= (next (control white))
    (true (control black)))
(<= (next (control black))
    (true (control white)))


(<= (legal ?x (drop ?c))
    (true (cell ?c 6 b))
    (true (control ?x)))
(<= (legal white noop)
        (true (control black)))
(<= (legal black noop)
    (true (control white)))


(<= (next (cell ?c ?r x))
    (does white (drop ?c))
    (top-unused ?c ?r))
(<= (next (cell ?c ?r o))
    (does black (drop ?c))
    (top-unused ?c ?r))


(<= (row ?x)
    (sequential ?a ?b ?c ?d)
    (true (cell ?a ?r ?x))
    (true (cell ?b ?r ?x))
    (true (cell ?c ?r ?x))
    (true (cell ?d ?r ?x)))
(<= (col  ?x)
    (sequential ?a ?b ?c ?d)
    (true (cell ?e ?a ?x))
    (true (cell ?e ?b ?x))
    (true (cell ?e ?c ?x))
    (true (cell ?e ?d ?x)))
(<= (diag1 ?x)
    (sequential ?a ?b ?c ?d)
    (sequential ?e ?f ?g ?h)
    (true (cell ?a ?e ?x))
    (true (cell ?b ?f ?x))
    (true (cell ?c ?g ?x))
    (true (cell ?d ?h ?x)))
(<= (diag2 ?x)
    (sequential ?a ?b ?c ?d)
    (sequential ?e ?f ?g ?h)
    (true (cell ?a ?h ?x))
    (true (cell ?b ?g ?x))
    (true (cell ?c ?f ?x))
    (true (cell ?d ?e ?x)))
(<= (connfour ?x)
    (or (col ?x)
        (row ?x)
        (diag1 ?x)
        (diag2 ?x)))


(<= (goal ?x 50)
    (not (connfour x))
    (not (connfour o))
    (role ?x))
(<= (goal white 100)
    (connfour x))
(<= (goal black 0)
    (connfour x))
(<= (goal white 0)
    (connfour o))
(<= (goal black 100)
    (connfour o))


(<= terminal
    (or (connfour x)
        (connfour o)))
(<= (not-filled)
    (true (cell ?c 6 b)))
(<= terminal
    (not (not-filled)))"""

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))



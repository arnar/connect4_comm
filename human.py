from SimpleXMLRPCServer import SimpleXMLRPCServer

import time

def log(str):
    print time.strftime("[%Y-%m-%dt%H:%M:%S]"), str

class Player(object):

    def __init__(self, role):
        log('Get ready to play, you are the %s player.' % role)   

    def get_state(self):
        return "human"
    
    state = property(get_state)

    def move(self, move):
        log("The opponent moved: " + move)
        return "human"

    def go(self):
        log("Your turn")
        t0 = time.time()
        themove = raw_input("Enter your move [abcdefg]: ").strip()
        t = time.time() - t0
        log("You took %.2f seconds to think" % t)
        return (themove, t, self.get_state())

    def retract(self):
        raise Exception("cannot retract human")

    def reset(self):
        raise Exception("cannot reset human")

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
        log("You have been terminated!")
        return 0

def main(role):
    p = Player(role)
    server = SimpleXMLRPCServer(("", 8000))
    server.register_instance(p)
    server.serve_forever()

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))



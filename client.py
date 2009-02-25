import pexpect

def main(player_exe):
    p = pexpect.spawn(player_exe)
    print "waiting for prompt"
    p.expect("> ")
    print "asking for state"
    p.sendline("p")
    print "waiting for prompt"
    p.expect("> ")
    print "got state", p.before
    print "quitting"
    p.sendline("q")

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))

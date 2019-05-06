import threading
import server
import argparse
import json
import globs
import neighbor


# set flags
parser = argparse.ArgumentParser()
# parser.add_argument("host", type=str, help="host")
# parser.add_argument("port", type=int, help="port")
parser.add_argument("configfile", type=str, help="configfile path")
args = parser.parse_args()

print(args.configfile)
# read config from json
# set globs here
# Open socket server
HOST = '127.0.0.1'
f = open(args.configfile, 'r')
config = json.load(f)
print(config)
f.close()

for n in config['neighbor_list']:
  globs.NEIGHBORS.append(
    neighbor.Neighbor(n['ip'], n['p2p_port'], n['user_port'])
  )

print(globs.NEIGHBORS.append)


def main():
  s1 = server.Server(HOST, config['p2p_port'], 'p2p')
  s2 = server.Server(HOST, config['user_port'], 'user')
  t1 = threading.Thread(target=s1.listen)
  t2 = threading.Thread(target=s2.listen)
  t1.start()
  t2.start()

main()
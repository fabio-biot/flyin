import sys
from models import StartHub, EndHub, Hub, Drone, Connection, Parser


    
def params(data):
    nb_drones = "nb_drones: x"
    start_hub = StartHub("start", 0, 0, max_drones, zone_type, color)
        

def main():
    path = sys.argv[1]
    parser = Parser("maps/easy/01_linear_path.txt")
    parser.parse()

if __name__ == "__main__":
    main()

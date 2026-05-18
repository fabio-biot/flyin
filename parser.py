from models import StartHub, EndHub, Hub, Drone, Connection, Parser


    
def params(data):
    nb_drones = "nb_drones: x"
    start_hub = StartHub("start", 0, 0, max_drones, zone_type, color)
        

def main():
    parser = Parser("maps/easy/01_linear_path.txt")
    network, nb_drones = parser.parse()
    print(f"network {network}")
    print(f"network {network.connections}")
    print(f"network {network.hubs['goal'].x}")
    print(f"nb drones {nb_drones}")

if __name__ == "__main__":
    main()

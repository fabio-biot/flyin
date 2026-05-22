from models import StartHub, Pathfinder

    
def params(data):
    nb_drones = "nb_drones: x"
    start_hub = StartHub("start", 0, 0, max_drones, zone_type, color)
        

def main():
    parser = Parser("maps/easy/02_simple_fork.txt")
    network, nb_drones = parser.parse()
    start_hub = network.start_hub
    end_hub = network.end_hub
    path_finder = Pathfinder()
    pathin = path_finder.find_path(start=start_hub, end=end_hub)
    for path in pathin:
        print(path.name)
    print(f"Start {start_hub.name}")
    print(f"End {end_hub.connections[0].hub1.name}")
    print(f"network {network}")
    for i in  range(len(network.connections)):
        print(f"Connection {i} = ")
        print(f"network {network.connections[i].hub1.name} à {network.connections[i].hub2.name}")
    print(f"network {network.hubs['goal'].x}")
    print(f"nb drones {nb_drones}")

if __name__ == "__main__":
    main()

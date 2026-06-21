from models import (
    Parser,
    Pathfinder,
    Drone,
    Simulation, 
    ParserError
)


def main():
    # Parse map
    file = "maps/easy/01_linear_path.txt"
    file2 = "maps/hard/03_ultimate_challenge.txt"
    try:
        parser = Parser(file2)
        network, nb_drones = parser.parse()
    except Exception as e:
        print(e)
        return

    print("=== MAP INFO ===")
    print(f"Start hub : {network.start_hub.name}")
    print(f"End hub   : {network.end_hub.name}")
    print(f"Nb drones : {nb_drones}")
    print()
    pathfinder = Pathfinder()
    print()
    drones = []

    for drone_id in range(1, nb_drones + 1):
        drones.append(
            Drone(
                drone_id,
                network.start_hub
            )
        )

    # print("=== DRONES ===")

    # for drone in drones:
    #     print(
    #         f"D{drone.id} at "
    #         f"{drone.current_hub.name}"
    #     )

    print()

    # Simulation test
    simulation = Simulation(
        network,
        drones,
        pathfinder
    )

    mode = "pygame"

    if mode == "pygame":
        from visualizer import Visualizer
        viz = Visualizer(network, simulation)
        viz.run()
    
    if mode == "cli":
        print("=== SIMULATION ===")
        try:
            simulation.run(pathfinder)
        except Exception as e:
            print(e)
            return
        print(simulation.turn)

if __name__ == "__main__":
    main()
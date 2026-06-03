from models import (
    Parser,
    Pathfinder,
    Drone,
    Simulation
)


def main():
    # Parse map
    parser = Parser("maps/medium/02_circular_loop.txt")
    network, nb_drones = parser.parse()

    print("=== MAP INFO ===")
    print(f"Start hub : {network.start_hub.name}")
    print(f"End hub   : {network.end_hub.name}")
    print(f"Nb drones : {nb_drones}")
    print()

    print("=== HUBS ===")
    for hub in network.hubs.values():
        print(
            f"{hub.name} "
            f"(zone={hub.zone_type}, "
            f"capacity={hub.max_drones})"
        )

    print()

    print("=== CONNECTIONS ===")
    for connection in network.connections:
        print(
            f"{connection.hub1.name}"
            f" <-> "
            f"{connection.hub2.name}"
        )

    print()

    # Pathfinder test
    pathfinder = Pathfinder()

    path = pathfinder.find_path(
        network.start_hub,
        network.end_hub
    )

    print("=== PATH FOUND ===")

    if path:
        print(
            " -> ".join(
                hub.name for hub in path
            )
        )

    print()

    # Create drones
    drones = []

    for drone_id in range(1, nb_drones + 1):
        drones.append(
            Drone(
                drone_id,
                network.start_hub
            )
        )

    print("=== DRONES ===")

    for drone in drones:
        print(
            f"D{drone.id} at "
            f"{drone.current_hub.name}"
        )

    print()

    # Simulation test
    simulation = Simulation(
        network,
        drones,
        pathfinder
    )

    print("=== SIMULATION ===")
    simulation.run(pathfinder)


if __name__ == "__main__":
    main()
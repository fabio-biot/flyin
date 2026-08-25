import argparse
from models import (
    Parser,
    Pathfinder,
    Drone,
    Simulation,
    Network
)


def build_simulation(
    network: Network,
    nb_drones: int
) -> tuple[Simulation, Pathfinder]:
    if network.start_hub is None:
        raise ValueError("Network has no start hub")
    pathfinder = Pathfinder()
    drones = [
        Drone(i, network.start_hub)
        for i in range(1, nb_drones + 1)
    ]

    return Simulation(network, drones, pathfinder), pathfinder


def run_cli(simulation: Simulation, pathfinder: Pathfinder) -> None:
    print("=== SIMULATION CLI ===")
    try:
        simulation.run(pathfinder)
    except Exception as e:
        print(e)


def run_pygame(network: Network, simulation: Simulation) -> None:
    from visualizer import Game

    game = Game(network, simulation)
    game.run()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Drone simulation"
    )

    parser.add_argument(
        "map",
        help="Path to the map file"
    )

    parser.add_argument(
        "mode",
        choices=["cli", "pygame"],
        help="Simulation mode"
    )

    args = parser.parse_args()

    try:
        map_parser = Parser(args.map)
        network, nb_drones = map_parser.parse()
    except Exception as e:
        print(f"Parser error: {e}")
        return

    if network.start_hub is None:
        print("Parser error: Network has no start hub")
        return

    if network.end_hub is None:
        print("Parser error: Network has no end hub")
        return

    print("=== MAP INFO ===")
    print(f"Start hub : {network.start_hub.name}")
    print(f"End hub   : {network.end_hub.name}")
    print(f"Nb drones : {nb_drones}")

    simulation, pathfinder = build_simulation(
        network,
        nb_drones
    )

    if args.mode == "pygame":
        run_pygame(network, simulation)

    elif args.mode == "cli":
        run_cli(simulation, pathfinder)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulation ended")

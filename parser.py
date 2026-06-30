from models import (
    Parser,
    Pathfinder,
    Drone,
    Simulation,
)

def get_mode():
    # mode = "cli"
    mode = "pygame"
    return mode

def build_simulation(network, nb_drones):
    pathfinder = Pathfinder()

    drones = [
        Drone(i, network.start_hub)
        for i in range(1, nb_drones + 1)
    ]

    return Simulation(network, drones, pathfinder), pathfinder


def run_cli(simulation, pathfinder):
    print("=== SIMULATION CLI ===")
    try:
        simulation.run(pathfinder)
    except Exception as e:
        print(e)


def run_pygame(network, simulation):
    from visualizer import Game

    game = Game(network, simulation)
    game.run()


def main():
    file = "maps/hard/02_capacity_hell.txt"

    try:
        parser = Parser(file)
        network, nb_drones = parser.parse()
    except Exception as e:
        print(f"Parser error: {e}")
        return

    print("=== MAP INFO ===")
    print(f"Start hub : {network.start_hub.name}")
    print(f"End hub   : {network.end_hub.name}")
    print(f"Nb drones : {nb_drones}")

    simulation, pathfinder = build_simulation(network, nb_drones)
    mode = get_mode()
    if mode == "pygame":
        run_pygame(network, simulation)

    elif mode == "cli":
        run_cli(simulation, pathfinder)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulation ended")

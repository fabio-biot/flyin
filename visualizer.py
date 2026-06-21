import pygame

pygame.init()

WIDTH, HEIGHT = 2000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Simulation")
clock = pygame.time.Clock()

class Visualizer:
    def __init__(self, network, simulation):
        self.network = network
        self.sim = simulation

    def draw_hub(self, hub):
        x = hub.x * 100 + 200
        y = hub.y * 100 + 200

        color = (0, 255, 0)

        pygame.draw.circle(screen, color, (x, y), 15)

    def draw_connections(self):
        for c in self.network.connections:
            x1, y1 = c.hub1.x * 100 + 200, c.hub1.y * 100 + 200
            x2, y2 = c.hub2.x * 100 + 200, c.hub2.y * 100 + 200

            pygame.draw.line(screen, (200, 200, 200), (x1, y1), (x2, y2), 2)
        
    def draw_drone(self, drone):
        if drone.in_transit:
            x = (drone.current_connection.hub1.x + drone.current_connection.hub2.x) / 2
            y = (drone.current_connection.hub1.y + drone.current_connection.hub2.y) / 2
        else:
            x = drone.current_hub.x
            y = drone.current_hub.y

        pygame.draw.circle(screen, (0, 0, 255), (int(x*100+200), int(y*100+200)), 8)


    def run(self):
        running = True

        while running:
            screen.fill((20, 20, 20))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            a = self.sim.compute_turn()
            self.sim.apply_moves(a)

            self.draw_connections()

            for hub in self.network.hubs.values():
                self.draw_hub(hub)

            for drone in self.sim.drones:
                self.draw_drone(drone)

            pygame.display.flip()
            clock.tick(2)
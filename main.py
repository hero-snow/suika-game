import pygame
import pymunk
import pymunk.pygame_util

# --- Constants ---
# Screen dimensions
WIDTH, HEIGHT = 600, 800
FPS = 60

# Colors
BACKGROUND_COLOR = (255, 255, 255)

# Physics properties
GRAVITY = (0.0, 900.0)

# Wall properties
WALL_INSET = 50
WALL_THICKNESS = 5
WALL_ELASTICITY = 0.5
WALL_FRICTION = 0.5

# Ball properties
BALL_MASS = 1
BALL_RADIUS = 30
BALL_ELASTICITY = 0.8
BALL_FRICTION = 0.5
BALL_SPAWN_Y = 50


# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Suika Game Base")
clock = pygame.time.Clock()

# --- Physics Space Setup ---
space = pymunk.Space()
space.gravity = GRAVITY

# Debug drawing tool
draw_options = pymunk.pygame_util.DrawOptions(screen)

# --- Wall Creation ---
def create_walls(space, width, height):
    """Creates static walls for the game area."""
    walls = [
        pymunk.Segment(space.static_body, (WALL_INSET, height - WALL_INSET), (width - WALL_INSET, height - WALL_INSET), WALL_THICKNESS), # Floor
        pymunk.Segment(space.static_body, (WALL_INSET, height - WALL_INSET), (WALL_INSET, WALL_INSET), WALL_THICKNESS),                 # Left wall
        pymunk.Segment(space.static_body, (width - WALL_INSET, height - WALL_INSET), (width - WALL_INSET, WALL_INSET), WALL_THICKNESS)  # Right wall
    ]
    for wall in walls:
        wall.elasticity = WALL_ELASTICITY
        wall.friction = WALL_FRICTION
    space.add(*walls)

# --- Ball Creation ---
def create_ball(space, x, y):
    """Creates a dynamic ball."""
    moment = pymunk.moment_for_circle(BALL_MASS, 0, BALL_RADIUS)
    body = pymunk.Body(BALL_MASS, moment)
    body.position = x, y
    shape = pymunk.Circle(body, BALL_RADIUS)
    shape.elasticity = BALL_ELASTICITY
    shape.friction = BALL_FRICTION
    space.add(body, shape)

# Generate walls
create_walls(space, WIDTH, HEIGHT)

# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, _ = event.pos
            # Restrict ball creation to within the walls
            if WALL_INSET < x < WIDTH - WALL_INSET:
                create_ball(space, x, BALL_SPAWN_Y)

    # 2. Physics Update
    space.step(1 / FPS)

    # 3. Drawing
    screen.fill(BACKGROUND_COLOR)
    space.debug_draw(draw_options) # Use Pymunk's debug drawing
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
import pygame
import pymunk
import pymunk.pygame_util
import random

# --- Constants ---
# Screen dimensions
WIDTH, HEIGHT = 600, 800
FPS = 60

# Colors
BACKGROUND_COLOR = (210, 230, 255)

# Physics properties
GRAVITY = (0.0, 900.0)

# Wall properties
WALL_INSET = 50
WALL_THICKNESS = 5
WALL_ELASTICITY = 0.5
WALL_FRICTION = 0.5

# Properties
MASS = 1
ELASTICITY = 0.8
FRICTION = 0.5
SPAWN_Y = 50

GAME_OVER_LINE_Y = 100  # Y coordinate of the game over line
GAME_OVER_DELAY = 2  # Grace period in seconds before game over

# Define animal specifications
# Evolution order: mouse -> rabbit -> cat -> dog -> fox -> horse -> giraffe -> lion -> elephant
ANIMAL_SPECS = [
    {"name": "mouse", "radius": 20, "color": (128, 128, 128), "evolves_to": "rabbit"},
    {"name": "rabbit", "radius": 25, "color": (255, 255, 255), "evolves_to": "cat"},
    {"name": "cat", "radius": 30, "color": (255, 165, 0), "evolves_to": "dog"},
    {"name": "dog", "radius": 35, "color": (139, 69, 19), "evolves_to": "fox"},
    {"name": "fox", "radius": 40, "color": (255, 140, 0), "evolves_to": "horse"},
    {"name": "horse", "radius": 50, "color": (160, 82, 45), "evolves_to": "giraffe"},
    {"name": "giraffe", "radius": 60, "color": (255, 215, 0), "evolves_to": "lion"},
    {"name": "lion", "radius": 70, "color": (218, 165, 32), "evolves_to": "elephant"},
    {
        "name": "elephant",
        "radius": 80,
        "color": (192, 192, 192),
        "evolves_to": None,
    },  # Elephants do not evolve
]

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Suika Game Base")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 100)
font_small = pygame.font.Font(None, 50)

# --- Physics Space Setup ---
space = pymunk.Space()
space.gravity = GRAVITY

# Debug drawing tool
draw_options = pymunk.pygame_util.DrawOptions(screen)


# --- Wall Creation ---
def create_walls(space, width, height):
    """Creates static walls for the game area."""
    walls = [
        pymunk.Segment(
            space.static_body,
            (WALL_INSET, height - WALL_INSET),
            (width - WALL_INSET, height - WALL_INSET),
            WALL_THICKNESS,
        ),  # Floor
        pymunk.Segment(
            space.static_body,
            (WALL_INSET, height - WALL_INSET),
            (WALL_INSET, WALL_INSET),
            WALL_THICKNESS,
        ),  # Left wall
        pymunk.Segment(
            space.static_body,
            (width - WALL_INSET, height - WALL_INSET),
            (width - WALL_INSET, WALL_INSET),
            WALL_THICKNESS,
        ),  # Right wall
    ]
    for wall in walls:
        wall.elasticity = WALL_ELASTICITY
        wall.friction = WALL_FRICTION
    space.add(*walls)


# --- Function to create an animal ---
def create_animal(space, x, y, animal_spec):
    radius = animal_spec["radius"]
    moment = pymunk.moment_for_circle(MASS, 0, radius)
    body = pymunk.Body(MASS, moment)
    body.position = x, y
    shape = pymunk.Circle(body, radius)
    shape.elasticity = ELASTICITY
    shape.friction = FRICTION
    # Add animal name as a custom property
    shape.animal_name = animal_spec["name"]
    shape.collision_type = 1  # Collision type for animals
    space.add(body, shape)
    return shape


# --- Collision Handler ---
# List for adding collided animals to the removal list
shapes_to_remove = []
# List for creating evolved animals
animals_to_add = []


def post_solve_collision(arbiter, space, data):
    global score
    # Get the two collided shapes
    shape_a, shape_b = arbiter.shapes

    # Check if both are animals
    if hasattr(shape_a, "animal_name") and hasattr(shape_b, "animal_name"):
        # Check if they are the same type of animal
        if shape_a.animal_name == shape_b.animal_name:
            # If already in the removal list, do not process
            if shape_a in shapes_to_remove or shape_b in shapes_to_remove:
                return

            # Check that it is not the final form that does not evolve (elephant)
            spec_a = get_animal_spec(shape_a.animal_name)
            if spec_a and spec_a["evolves_to"]:
                # Add the two animals to the removal list
                shapes_to_remove.append(shape_a)
                shapes_to_remove.append(shape_b)

                # Calculate the collision position (midpoint)
                pos_a = shape_a.body.position
                pos_b = shape_b.body.position
                collision_pos = (pos_a + pos_b) / 2

                # Get the specification of the evolved animal and add it to the addition list
                evolved_spec = get_animal_spec(spec_a["evolves_to"])
                if evolved_spec:
                    animals_to_add.append(
                        (collision_pos.x, collision_pos.y, evolved_spec)
                    )
                    # Add score
                    for i, spec in enumerate(ANIMAL_SPECS):
                        if spec["name"] == evolved_spec["name"]:
                            score += (
                                i * 10 + 10
                            )  # Add score based on the evolved animal
                            break


# Register the collision handler with Pymunk
handler = space.on_collision(
    1, 1, post_solve=post_solve_collision
)  # Collision between two objects of collision type 1

# Create walls
create_walls(space, WIDTH, HEIGHT)

# --- Helpers ---
# Dictionary for looking up animal specifications by name
ANIMAL_MAP = {spec["name"]: spec for spec in ANIMAL_SPECS}


def get_animal_spec(animal_name):
    return ANIMAL_MAP.get(animal_name)


# --- Main Game Loop ---
running = True
game_over = False
game_over_timer = 0
is_animal_over_line = False
score = 0
high_score = 0

# Load high score
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except (FileNotFoundError, ValueError):
    high_score = 0


# Randomly select the first animal to drop from the first 3 types
current_animal_spec = random.choice(ANIMAL_SPECS[:3])


def reset_game():
    """Resets the game to its initial state."""
    global game_over, game_over_timer, is_animal_over_line, current_animal_spec, score

    # Remove all animals from the space
    bodies_to_remove = [
        body for body in space.bodies if body.body_type == pymunk.Body.DYNAMIC
    ]
    for body in bodies_to_remove:
        space.remove(body, *body.shapes)

    # Clear collision handling lists
    shapes_to_remove.clear()
    animals_to_add.clear()

    # Reset game state variables
    game_over = False
    game_over_timer = 0
    is_animal_over_line = False
    score = 0

    # Set a new starting animal
    current_animal_spec = random.choice(ANIMAL_SPECS[:3])


while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # When clicked, drop the current animal at that location (only if not game over)
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            x, _ = event.pos
            radius = current_animal_spec["radius"]
            # Restrict the X coordinate so that it does not go outside the wall
            x = max(50 + radius, min(x, WIDTH - 50 - radius))

            create_animal(space, x, 50, current_animal_spec)  # Drop from Y=50

            # Randomly select the next animal to drop
            current_animal_spec = random.choice(ANIMAL_SPECS[:3])
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    # 2. Physics Update
    space.step(1 / FPS)

    # Deletion and addition of objects after collision
    for shape in shapes_to_remove:
        if shape.body in space.bodies:
            space.remove(shape.body, shape)
    shapes_to_remove.clear()

    for x, y, spec in animals_to_add:
        create_animal(space, x, y, spec)
    animals_to_add.clear()

    # Game over judgment
    if not game_over:
        is_animal_over_line = False
        for body in space.bodies:
            # Check if the top of the animal is over the line
            shapes_list = list(body.shapes)

            if shapes_list:
                first_shape = shapes_list[0]
            if body.position.y - first_shape.radius < GAME_OVER_LINE_Y:
                is_animal_over_line = True
                break

        if is_animal_over_line:
            game_over_timer += 1 / FPS
            if game_over_timer > GAME_OVER_DELAY:
                game_over = True
                # Update high score
                if score > high_score:
                    high_score = score
                    with open("highscore.txt", "w") as f:
                        f.write(str(high_score))
        else:
            game_over_timer = 0

    # 3. Drawing
    screen.fill((BACKGROUND_COLOR))  # Background color
    space.debug_draw(draw_options)  # Use Pymunk's debug drawing
    # Drawing the game over line (dotted line)
    for x in range(50, WIDTH - 50, 20):
        pygame.draw.line(
            screen, (255, 0, 0), (x, GAME_OVER_LINE_Y), (x + 10, GAME_OVER_LINE_Y), 2
        )

    # Drawing the walls
    for wall in space.static_body.shapes:
        pygame.draw.line(screen, (100, 100, 100), wall.a, wall.b, 5)

    # Drawing the animals (circles)
    for body in space.bodies:
        for shape in body.shapes:
            if hasattr(shape, "animal_name"):
                spec = get_animal_spec(shape.animal_name)
                if spec:
                    pos = body.position
                    pygame.draw.circle(
                        screen, spec["color"], (int(pos.x), int(pos.y)), spec["radius"]
                    )

    # Display the next animal to be dropped at the mouse cursor position (if not game over)
    if not game_over:
        mouse_x, _ = pygame.mouse.get_pos()
        radius = current_animal_spec["radius"]
        # Restrict the X coordinate to the inside of the wall
        indicator_x = max(50 + radius, min(mouse_x, WIDTH - 50 - radius))
        pygame.draw.circle(
            screen, current_animal_spec["color"], (indicator_x, 50), radius, 3
        )  # Draw only the border

    # Display score
    score_text = font_small.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (60, 20))

    # Display high score
    high_score_text = font_small.render(f"High Score: {high_score}", True, (0, 0, 0))
    high_score_rect = high_score_text.get_rect(right=WIDTH - 60, top=20)
    screen.blit(high_score_text, high_score_rect)

    # Display game over
    if game_over:
        text = font_large.render("Game Over", True, (200, 0, 0))
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40))
        screen.blit(text, text_rect)

        # Final score
        final_score_text = font_small.render(f"Score: {score}", True, (0, 0, 0))
        final_score_rect = final_score_text.get_rect(
            center=(WIDTH / 2, HEIGHT / 2 + 20)
        )
        screen.blit(final_score_text, final_score_rect)

        # Restart message
        restart_text = font_small.render("Press R to Restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 70))
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

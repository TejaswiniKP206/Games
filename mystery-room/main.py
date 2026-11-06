
import pygame
import math

pygame.init()

# ---------------- SETTINGS ----------------

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mystery Room | Case 001")
clock = pygame.time.Clock()

TITLE = pygame.font.SysFont("georgia", 48, bold=True)
HEADING = pygame.font.SysFont("georgia", 27, bold=True)
FONT = pygame.font.SysFont("arial", 19)
SMALL = pygame.font.SysFont("arial", 15)

# ---------------- COLORS ----------------

BG = (15, 18, 26)
PANEL = (29, 32, 42)
GOLD = (218, 174, 91)
CREAM = (238, 226, 204)
MUTED = (160, 158, 153)
WOOD = (91, 57, 39)
DARK_WOOD = (53, 35, 29)
FLOOR = (78, 54, 43)
WHITE = (245, 242, 232)

# ---------------- GAME DATA ----------------

player = pygame.Rect(120, 490, 28, 38)
speed = 4

# Furniture that blocks movement
obstacles = [
    pygame.Rect(280, 220, 190, 85),
    pygame.Rect(690, 170, 105, 210),
    pygame.Rect(500, 405, 120, 65),
]

# Interactive clues
clues = [
    {
        "name": "Desk Documents",
        "rect": pygame.Rect(335, 230, 75, 35),
        "message": "You found a torn document. It mentions a secret meeting at midnight.",
        "found": False
    },
    {
        "name": "Bookshelf",
        "rect": pygame.Rect(705, 200, 75, 155),
        "message": "A book is out of place. Behind it, you find a small golden key.",
        "found": False
    },
    {
        "name": "Small Table",
        "rect": pygame.Rect(515, 415, 90, 40),
        "message": "There is a photograph. Someone was standing near the diamond cabinet.",
        "found": False
    }
]

# Clue discovery popup
popup_clue = None
popup_timer = 0
POPUP_DURATION = 300

state = "menu"
show_guide = False
show_notebook = False

# ---------------- HELPERS ----------------

def draw_text(text, font, color, x, y, center=False):
    image = font.render(text, True, color)
    rect = image.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(image, rect)


def panel(rect, color=PANEL, border=GOLD):
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, border, rect, 2, border_radius=12)


def button(label, rect):
    mouse = pygame.mouse.get_pos()
    color = (95, 72, 48) if rect.collidepoint(mouse) else (57, 48, 40)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, GOLD, rect, 2, border_radius=8)
    draw_text(label, FONT, CREAM, rect.centerx, rect.centery, True)


# ---------------- MAIN MENU ----------------

def draw_menu():
    screen.fill(BG)

    # Decorative background
    for i in range(12):
        pygame.draw.circle(
            screen, (25, 29, 38),
            (i * 95, 100 + int(math.sin(i) * 20)), 35
        )

    draw_text("CASE FILE NO. 001", SMALL, GOLD, 500, 150, True)
    draw_text("MYSTERY ROOM", TITLE, CREAM, 500, 220, True)
    draw_text("THE MISSING DIAMOND", HEADING, GOLD, 500, 280, True)

    draw_text(
        "A secret is hidden inside this room.",
        FONT, MUTED, 500, 330, True
    )

    start = pygame.Rect(380, 405, 240, 48)
    guide = pygame.Rect(380, 470, 240, 48)
    quit_btn = pygame.Rect(380, 535, 240, 48)

    button("START INVESTIGATION", start)
    button("HOW TO PLAY", guide)
    button("EXIT", quit_btn)

    return start, guide, quit_btn

def draw_clue_popup(clue, timer):
    if clue is None:
        return

    # Slide in and slide out animation
    progress = min(1, (POPUP_DURATION - timer) / 20)

    if timer < 25:
        progress = min(progress, timer / 25)

    # Smooth animation
    progress = progress * progress * (3 - 2 * progress)

    card_width = 320
    card_height = 175

    target_x = WIDTH - card_width - 25
    x = int(WIDTH + 10 - (WIDTH - target_x) * progress)
    y = HEIGHT - card_height - 75

    card = pygame.Rect(x, y, card_width, card_height)

    # Shadow
    shadow = pygame.Surface((card_width + 10, card_height + 10),
                             pygame.SRCALPHA)
    pygame.draw.rect(
        shadow, (0, 0, 0, 110),
        (5, 5, card_width, card_height),
        border_radius=12
    )
    screen.blit(shadow, (x - 5, y - 5))

    # Card background and border
    pygame.draw.rect(screen, (32, 29, 30), card, border_radius=12)
    pygame.draw.rect(screen, GOLD, card, 2, border_radius=12)

    # Gold accent strip
    pygame.draw.rect(
        screen, GOLD,
        (x, y + 12, 5, card_height - 24),
        border_radius=3
    )

    # Card content
    draw_text("✦  CLUE DISCOVERED", SMALL, GOLD, x + 20, y + 18)
    draw_text(clue["name"], HEADING, CREAM, x + 20, y + 52)

    # Description wrapped across multiple lines
    words = clue["message"].split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word

        if SMALL.size(test_line)[0] > card_width - 40:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line.strip()

    if current_line:
        lines.append(current_line)

    for i, line in enumerate(lines[:3]):
        draw_text(line, SMALL, MUTED, x + 20, y + 95 + i * 21)

    draw_text("EVIDENCE ADDED TO NOTEBOOK", SMALL,
              GOLD, x + 20, y + 145)


# ---------------- GUIDE SCREEN ----------------

def draw_guide():
    screen.fill(BG)

    panel(pygame.Rect(130, 65, 740, 570))

    draw_text("DETECTIVE'S GUIDE", TITLE, GOLD, 500, 115, True)
    draw_text("CASE 001: THE MISSING DIAMOND", HEADING, CREAM, 500, 170, True)

    instructions = [
        ("YOUR MISSION", "A priceless diamond has mysteriously disappeared."),
        ("STEP 1", "Explore the room and search for suspicious objects."),
        ("STEP 2", "Stand near an object and press E to investigate."),
        ("STEP 3", "Collect all three clues hidden in the room."),
        ("STEP 4", "Press N to open your detective notebook."),
        ("FINAL TASK", "Find the evidence and uncover what happened."),
    ]

    y = 230
    for heading, description in instructions:
        draw_text(heading, FONT, GOLD, 205, y)
        draw_text(description, SMALL, CREAM, 205, y + 29)
        y += 63

    draw_text(
        "MOVEMENT: WASD / ARROW KEYS     INTERACT: E     NOTEBOOK: N",
        SMALL, MUTED, 500, 570, True
    )

    back = pygame.Rect(380, 595, 240, 35)
    button("BACK TO MENU", back)
    return back


# ---------------- DRAW ROOM ----------------

def draw_room():
    screen.fill(BG)

    # Wall
    pygame.draw.rect(screen, (43, 39, 42), (45, 65, 910, 170))
    pygame.draw.rect(screen, GOLD, (45, 65, 910, 170), 2)

    # Floor
    pygame.draw.rect(screen, FLOOR, (45, 235, 910, 415))

    # Floorboard details
    for y in range(250, 650, 55):
        pygame.draw.line(screen, (100, 70, 55), (45, y), (955, y), 1)

    for x in range(45, 955, 110):
        pygame.draw.line(screen, (100, 70, 55), (x, 235), (x, 650), 1)

    # Wall painting
    pygame.draw.rect(screen, DARK_WOOD, (110, 95, 145, 105))
    pygame.draw.rect(screen, GOLD, (110, 95, 145, 105), 4)
    pygame.draw.rect(screen, (69, 84, 75), (122, 107, 121, 81))
    pygame.draw.circle(screen, GOLD, (182, 145), 24)

    # Desk
    pygame.draw.rect(screen, DARK_WOOD, (280, 220, 190, 85))
    pygame.draw.rect(screen, WOOD, (280, 215, 190, 18))
    pygame.draw.rect(screen, GOLD, (280, 220, 190, 85), 2)

    # Papers on desk
    pygame.draw.rect(screen, CREAM, (335, 230, 75, 35))
    pygame.draw.line(screen, MUTED, (345, 241), (400, 241), 1)
    pygame.draw.line(screen, MUTED, (345, 249), (390, 249), 1)

    # Desk lamp
    pygame.draw.line(screen, GOLD, (440, 190), (440, 215), 5)
    pygame.draw.polygon(
        screen, GOLD,
        [(422, 190), (458, 190), (450, 172), (430, 172)]
    )

    # Bookshelf
    pygame.draw.rect(screen, DARK_WOOD, (690, 170, 105, 210))
    pygame.draw.rect(screen, GOLD, (690, 170, 105, 210), 3)

    book_colors = [
        (135, 55, 60), (54, 91, 119),
        (181, 137, 68), (71, 112, 78),
        (118, 78, 126)
    ]

    for i, color in enumerate(book_colors):
        pygame.draw.rect(
            screen, color, (700 + i * 18, 190, 15, 70)
        )
        pygame.draw.rect(
            screen, color, (700 + i * 18, 280, 15, 75)
        )

    # Small table
    pygame.draw.rect(screen, DARK_WOOD, (500, 405, 120, 65))
    pygame.draw.rect(screen, WOOD, (500, 400, 120, 12))
    pygame.draw.rect(screen, GOLD, (500, 405, 120, 65), 2)

    # Rug
    pygame.draw.rect(screen, (91, 35, 44), (250, 500, 400, 125))
    pygame.draw.rect(screen, GOLD, (260, 510, 380, 105), 2)

    # Exit door
    pygame.draw.rect(screen, DARK_WOOD, (860, 370, 70, 175))
    pygame.draw.rect(screen, GOLD, (860, 370, 70, 175), 3)
    pygame.draw.circle(screen, GOLD, (915, 460), 5)
    draw_text("EXIT", SMALL, GOLD, 875, 345)

    # Side lamp glow effect
    glow = pygame.Surface((240, 180), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 190, 90, 22), (0, 0, 240, 180))
    screen.blit(glow, (335, 150))


# ---------------- PLAYER ----------------

def draw_player():
    pygame.draw.ellipse(
        screen, (20, 18, 18),
        (player.x - 3, player.bottom - 5, 35, 12)
    )

    pygame.draw.rect(
        screen, (45, 85, 115), player,
        border_radius=8
    )

    pygame.draw.circle(
        screen, (222, 178, 139),
        (player.centerx, player.y + 3), 12
    )

    pygame.draw.circle(
        screen, (25, 25, 25),
        (player.centerx - 4, player.y + 2), 2
    )

    pygame.draw.circle(
        screen, (25, 25, 25),
        (player.centerx + 4, player.y + 2), 2
    )


# ---------------- INTERACTIONS ----------------

def nearby_clue():
    player_center = pygame.Vector2(player.center)

    for clue in clues:
        if clue["found"]:
            continue

        clue_center = pygame.Vector2(clue["rect"].center)

        if player_center.distance_to(clue_center) <= 110:
            return clue

    return None


def draw_clue_highlights():
    for clue in clues:
        if not clue["found"]:
            pygame.draw.rect(
                screen, GOLD, clue["rect"], 2, border_radius=4
            )


def draw_hud():
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 55))
    draw_text("CASE 001", FONT, GOLD, 25, 15)
    draw_text("THE MISSING DIAMOND", FONT, CREAM, 145, 15)

    found = sum(clue["found"] for clue in clues)
    draw_text(f"CLUES: {found}/3", FONT, GOLD, 800, 15)

    # Message bar
    pygame.draw.rect(screen, PANEL, (45, 655, 910, 35))
    draw_text(message, SMALL, CREAM, 60, 663)


def draw_notebook():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    panel(pygame.Rect(230, 110, 540, 470))

    draw_text("DETECTIVE NOTEBOOK", TITLE, GOLD, 500, 160, True)
    draw_text("Collected Evidence", HEADING, CREAM, 500, 220, True)

    y = 280
    for clue in clues:
        status = "FOUND" if clue["found"] else "NOT FOUND"
        color = (110, 190, 120) if clue["found"] else MUTED
        draw_text(clue["name"], FONT, CREAM, 290, y)
        draw_text(status, SMALL, color, 640, y + 3)
        y += 55

    draw_text("Press N to close notebook", SMALL, GOLD, 500, 530, True)


# ---------------- MAIN LOOP ----------------


message = "Explore the room. Press E near objects to investigate."
message_timer = 0

popup_clue = None
popup_timer = 0
POPUP_DURATION = 300

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if state == "game":
                if event.key == pygame.K_ESCAPE:
                    state = "menu"

                elif event.key == pygame.K_n:
                    show_notebook = not show_notebook

                elif event.key == pygame.K_e and not show_notebook:
                    clue = nearby_clue()

                    if clue:
                        clue["found"] = True
                        popup_clue = clue
                        popup_timer = POPUP_DURATION
                        message = "A new clue was added to your notebook."
                        message_timer = 180
                    else:
                        message = "Nothing interesting nearby. Keep exploring."
                        message_timer = 180

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "menu":
                start, guide, quit_btn = draw_menu()

                if start.collidepoint(event.pos):
                    state = "game"
                elif guide.collidepoint(event.pos):
                    state = "guide"
                elif quit_btn.collidepoint(event.pos):
                    running = False

            elif state == "guide":
                back = pygame.Rect(380, 595, 240, 35)
                if back.collidepoint(event.pos):
                    state = "menu"

    # ---------------- UPDATE GAME ----------------

    if state == "game" and not show_notebook:
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -4
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 4
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -4
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 4

        player.x += dx

        for obstacle in obstacles:
            if player.colliderect(obstacle):
                if dx > 0:
                    player.right = obstacle.left
                elif dx < 0:
                    player.left = obstacle.right

        player.y += dy

        for obstacle in obstacles:
            if player.colliderect(obstacle):
                if dy > 0:
                    player.bottom = obstacle.top
                elif dy < 0:
                    player.top = obstacle.bottom

        player.clamp_ip(pygame.Rect(45, 235, 910, 415))

    # Update clue popup animation timer
    if popup_timer > 0:
        popup_timer -= 1
    else:
        popup_clue = None

    if message_timer > 0:
        message_timer -= 1
    elif state == "game":
        message = "Explore the room. Press E near objects to investigate."

    # ---------------- DRAW ----------------

    if state == "menu":
        draw_menu()

    elif state == "guide":
        draw_guide()

    elif state == "game":
        draw_room()
        draw_clue_highlights()
        draw_player()
        draw_hud()

        clue = nearby_clue()
        if clue and not show_notebook:
            draw_text(
                f"Press E to investigate: {clue['name']}",
                FONT, GOLD, WIDTH // 2, 615, True
            )

        if show_notebook:
            draw_notebook()
        elif popup_clue is not None:
            draw_clue_popup(popup_clue, popup_timer)

    pygame.display.flip()

pygame.quit()

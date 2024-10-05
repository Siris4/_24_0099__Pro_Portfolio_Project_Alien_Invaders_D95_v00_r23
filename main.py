import tkinter as tk
from PIL import Image, ImageTk
import random
import os

# Set up the main window
root = tk.Tk()
root.title("Space Invaders")
root.resizable(False, False)
root.geometry("800x600")

# Create the canvas for the game
canvas = tk.Canvas(root, width=800, height=600, bg="black")
canvas.pack()

# File to store the high score
high_score_file = "highscore.txt"

# Function to load high score from file
def load_high_score():
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as f:
            return int(f.read().strip())
    return 0

# Function to save high score to file
def save_high_score(new_high_score):
    with open(high_score_file, "w") as f:
        f.write(str(new_high_score))

# Load the high score from the file
high_score = load_high_score()

# Score, high score, lives, and level variables
score = 0
lives = 3
level = 1
top_row_points = 300
middle_row_points = 200
bottom_row_points = 100
round_multiplier = 1.1

# Spaceship properties
spaceship_x = 380
spaceship_y = 550
spaceship_speed = 5
spaceship_move_direction = 0

# Create the spaceship using the image
spaceship_image = Image.open(
    r"C:\Users\Siris\Desktop\GitHub Projects 100 Days NewB\_24_0099__Day95_Pro_Portfolio_Project_Alien_Invaders__241001\NewProject\r00_env_START\r21\spaceship.png")
spaceship_image = spaceship_image.resize((40, 40), Image.Resampling.LANCZOS)
spaceship_photo = ImageTk.PhotoImage(spaceship_image)
spaceship = canvas.create_image(spaceship_x, spaceship_y, image=spaceship_photo, anchor="nw")

# Load the splat image for alien explosion
splat_image = Image.open(
    r"C:\Users\Siris\Desktop\GitHub Projects 100 Days NewB\_24_0099__Day95_Pro_Portfolio_Project_Alien_Invaders__241001\NewProject\r00_env_START\r21\splat_only.png")
splat_image = splat_image.resize((40, 40), Image.Resampling.LANCZOS)
splat_photo = ImageTk.PhotoImage(splat_image)

# Variable to keep track of the active bullet
active_bullet = None

# Lists to track barriers, aliens, and bombs
barriers = []
aliens = []
active_bombs = []

# Alien movement properties
alien_move_direction = 1
alien_speed = 10
alien_move_down = 1
alien_move_interval = 500  # Interval for alien movement
bomb_drop_interval = 1000  # Interval for bomb drop

# Bomb properties
max_bombs = 8

# Flag to check if a side has been hit
edge_hit = False

# Display score, high score, lives, and level
score_label = canvas.create_text(100, 20, text=f"Score: {score}", fill="white", font=("Retro Gaming", 16))
high_score_label = canvas.create_text(700, 20, text=f"High Score: {high_score}", fill="white", font=("Retro Gaming", 16))
lives_label = canvas.create_text(400, 20, text=f"Lives: {lives}", fill="white", font=("Retro Gaming", 16))
level_label = None  # Level display will be created dynamically

# Function to update score, high score, lives, and level
def update_labels():
    global score, high_score, lives, level
    canvas.itemconfig(score_label, text=f"Score: {score}")
    canvas.itemconfig(high_score_label, text=f"High Score: {high_score}")
    canvas.itemconfig(lives_label, text=f"Lives: {lives}")

# Function to show the current level on the screen
def show_level():
    global level_label
    if level_label:
        canvas.delete(level_label)
    level_label = canvas.create_text(400, 300, text=f"Level {level}", fill="yellow", font=("Retro Gaming", 32))
    root.after(2000, lambda: canvas.delete(level_label))  # Remove the level label after 2 seconds

# Function to end the game
def game_over():
    canvas.create_text(400, 300, text="Game Over", fill="red", font=("Retro Gaming", 32))

# Function to drop alien bombs
def drop_alien_bombs():
    if len(active_bombs) < max_bombs:
        columns_with_aliens = {}
        for alien in aliens:
            alien_x = min([canvas.coords(pixel)[0] for pixel in alien[2]])
            if alien_x not in columns_with_aliens or columns_with_aliens[alien_x][1] < alien[1]:
                columns_with_aliens[alien_x] = alien
        if columns_with_aliens:
            selected_column = random.choice(list(columns_with_aliens.values()))
            alien_x = min([canvas.coords(pixel)[0] for pixel in selected_column[2]])
            alien_y = max([canvas.coords(pixel)[1] for pixel in selected_column[2]])
            bomb = canvas.create_rectangle(alien_x + 20 - 2, alien_y + 5, alien_x + 20 + 2, alien_y + 15, fill="red")
            active_bombs.append(bomb)
            move_bomb(bomb)
    root.after(bomb_drop_interval, drop_alien_bombs)

# Function to move the bomb
def move_bomb(bomb):
    bomb_coords = canvas.coords(bomb)
    if bomb_coords[1] >= 600:
        canvas.delete(bomb)
        active_bombs.remove(bomb)
    else:
        canvas.move(bomb, 0, 5)
        check_bomb_collision(bomb)
        root.after(50, lambda: move_bomb(bomb))

# Function to check if a bomb hits a barrier, the spaceship, or a bullet
def check_bomb_collision(bomb):
    global active_bullet, lives
    bomb_coords = canvas.coords(bomb)
    bomb_x = bomb_coords[0] + 2
    bomb_y = bomb_coords[1]

    for barrier_item in barriers:
        pixel_x, pixel_y, pixel_rectangle = barrier_item
        if pixel_x <= bomb_x <= pixel_x + 5 and pixel_y <= bomb_y <= pixel_y + 5:
            canvas.delete(pixel_rectangle)
            barriers.remove(barrier_item)
            canvas.delete(bomb)
            active_bombs.remove(bomb)
            return

    spaceship_coords = canvas.coords(spaceship)
    spaceship_x1, spaceship_y1, spaceship_x2, spaceship_y2 = spaceship_coords[0], spaceship_coords[1], spaceship_coords[0] + 40, spaceship_coords[1] + 40
    if spaceship_x1 <= bomb_x <= spaceship_x2 and spaceship_y1 <= bomb_y <= spaceship_y2:
        lives -= 1
        update_labels()
        canvas.delete(bomb)
        active_bombs.remove(bomb)
        splat = canvas.create_image(spaceship_x1, spaceship_y1, image=splat_photo, anchor="nw")
        root.after(1000, canvas.delete, splat)
        if lives == 0:
            game_over()
        return

    if active_bullet is not None:
        bullet_coords = canvas.coords(active_bullet)
        bullet_x = bullet_coords[0] + 2
        bullet_y = bullet_coords[1]
        if bullet_x == bomb_x and bullet_y <= bomb_y:
            canvas.delete(bomb)
            active_bombs.remove(bomb)
            canvas.delete(active_bullet)
            active_bullet = None
            return

# Function to move the spaceship left or right
def move_spaceship():
    x1, y1 = canvas.coords(spaceship)
    if spaceship_move_direction == -1 and x1 > 0:
        canvas.move(spaceship, -spaceship_speed, 0)
    elif spaceship_move_direction == 1 and x1 < 760:
        canvas.move(spaceship, spaceship_speed, 0)
    root.after(20, move_spaceship)

# Movement functions for spaceship
def start_move_left(event):
    global spaceship_move_direction
    spaceship_move_direction = -1

def start_move_right(event):
    global spaceship_move_direction
    spaceship_move_direction = 1

def stop_move(event):
    global spaceship_move_direction
    spaceship_move_direction = 0

# Function to fire a bullet
def fire_bullet(event):
    global active_bullet
    if active_bullet is not None:
        return
    x1, y1 = canvas.coords(spaceship)
    bullet = canvas.create_rectangle(x1 + 20 - 2, y1 - 10, x1 + 20 + 2, y1, fill="white")
    active_bullet = bullet
    move_bullet()

# Function to move the bullet
def move_bullet():
    global active_bullet
    if active_bullet is not None:
        try:
            bullet_coords = canvas.coords(active_bullet)
        except tk.TclError:
            return
        canvas.move(active_bullet, 0, -10)
        check_collision()
        if bullet_coords[1] < 0:
            canvas.delete(active_bullet)
            active_bullet = None
    if active_bullet is not None:
        root.after(50, move_bullet)

# Function to check if a bullet hits an alien or barrier
def check_collision():
    global active_bullet, score, high_score
    if active_bullet is None:
        return
    bullet_coords = canvas.coords(active_bullet)
    bullet_x = bullet_coords[0] + 2
    bullet_y = bullet_coords[1]
    for alien in aliens:
        alien_x = min([canvas.coords(pixel)[0] for pixel in alien[2]])
        alien_y = min([canvas.coords(pixel)[1] for pixel in alien[2]])
        if alien_x <= bullet_x <= alien_x + 40 and alien_y <= bullet_y <= alien_y + 40:
            for pixel_rectangle in alien[2]:
                canvas.delete(pixel_rectangle)
            aliens.remove(alien)
            splat = canvas.create_image(alien_x, alien_y, image=splat_photo, anchor="nw")
            root.after(1000, canvas.delete, splat)
            canvas.delete(active_bullet)
            active_bullet = None
            if alien[0] == 50:
                score += top_row_points
            elif alien[0] == 150:
                score += middle_row_points
            else:
                score += bottom_row_points
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            update_labels()
            if not aliens:
                start_new_round()
            return

    for barrier_item in barriers:
        pixel_x, pixel_y, pixel_rectangle = barrier_item
        if pixel_x <= bullet_x <= pixel_x + 5 and pixel_y <= bullet_y <= bullet_y + 5:
            canvas.delete(pixel_rectangle)
            barriers.remove(barrier_item)
            canvas.delete(active_bullet)
            active_bullet = None
            return

# Function to create barriers
def create_barriers():
    barrier_y = spaceship_y - 150
    barrier_spacing = 160
    pixel_size = 5
    barrier_shape = [
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
    ]
    for i in range(4):
        barrier_x = 130 + i * barrier_spacing
        for row in range(len(barrier_shape)):
            for col in range(len(barrier_shape[0])):
                if barrier_shape[row][col] == 1:
                    pixel_rectangle = canvas.create_rectangle(
                        barrier_x + col * pixel_size, barrier_y + row * pixel_size,
                        barrier_x + (col + 1) * pixel_size, barrier_y + (row + 1) * pixel_size,
                        fill="green", outline="")
                    barriers.append([barrier_x + col * pixel_size, barrier_y + row * pixel_size, pixel_rectangle])

# Function to create aliens
def create_aliens():
    alien_spacing = 80
    pixel_size = 5
    alien1_shape = [
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, 0, 1, 0],
    ]
    alien2_shape = [
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 0, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 0, 0, 1],
    ]
    for row_num in range(2):
        alien_y = 50 + row_num * 50
        for i in range(8):
            alien_x = 50 + i * alien_spacing
            alien_pixels = []
            for row in range(len(alien1_shape)):
                for col in range(len(alien1_shape[0])):
                    if alien1_shape[row][col] == 1:
                        pixel_rectangle = canvas.create_rectangle(
                            alien_x + col * pixel_size, alien_y + row * pixel_size,
                            alien_x + (col + 1) * pixel_size, alien_y + (row + 1) * pixel_size,
                            fill="green", outline="")
                        alien_pixels.append(pixel_rectangle)
            aliens.append([alien_x, alien_y, alien_pixels])

    alien_y = 150
    for i in range(8):
        alien_x = 50 + i * alien_spacing
        alien_pixels = []
        for row in range(len(alien2_shape)):
            for col in range(len(alien2_shape[0])):
                if alien2_shape[row][col] == 1:
                    pixel_rectangle = canvas.create_rectangle(
                        alien_x + col * pixel_size, alien_y + row * pixel_size,
                        alien_x + (col + 1) * pixel_size, alien_y + (row + 1) * pixel_size,
                        fill="green", outline="")
                    alien_pixels.append(pixel_rectangle)
        aliens.append([alien_x, alien_y, alien_pixels])

# Function to move aliens left and right, then down by 1 pixel
def move_aliens():
    global alien_move_direction, edge_hit
    leftmost_x = min([min([canvas.coords(pixel)[0] for pixel in alien[2]]) for alien in aliens])
    rightmost_x = max([max([canvas.coords(pixel)[0] for pixel in alien[2]]) for alien in aliens])
    for alien in aliens:
        for pixel_rectangle in alien[2]:
            canvas.move(pixel_rectangle, alien_speed * alien_move_direction, 0)
    if not edge_hit and (leftmost_x <= 0 or rightmost_x >= 800):
        alien_move_direction *= -1
        edge_hit = True
        for alien in aliens:
            for pixel_rectangle in alien[2]:
                canvas.move(pixel_rectangle, 0, alien_move_down)
    if edge_hit and 0 < leftmost_x < 800 and 0 < rightmost_x < 800:
        edge_hit = False
    root.after(alien_move_interval, move_aliens)

# Function to create and animate stars
def create_stars():
    for _ in range(3):
        x_star = random.randint(0, 800)
        y_star = 0
        star = canvas.create_rectangle(x_star, y_star, x_star + 1, y_star + 1, fill="yellow")
        move_star(star)

def move_star(star):
    star_coords = canvas.coords(star)
    if star_coords[1] >= 600:
        canvas.delete(star)
    else:
        canvas.move(star, 0, 1)
        root.after(150, lambda: move_star(star))

# Function to start a new round, reset barriers and aliens, and display the new level
def start_new_round():
    global top_row_points, middle_row_points, bottom_row_points, level, alien_move_interval, bomb_drop_interval
    level += 1
    show_level()  # Show the new level on the screen
    top_row_points = int(top_row_points * round_multiplier)
    middle_row_points = int(middle_row_points * round_multiplier)
    bottom_row_points = int(bottom_row_points * round_multiplier)
    alien_move_interval = int(alien_move_interval * 0.92)  # Increase alien speed by 8%
    bomb_drop_interval = int(bomb_drop_interval * 0.92)  # Increase bomb dropping speed by 8%
    # Reset barriers and aliens
    for barrier_item in barriers:
        canvas.delete(barrier_item[2])
    barriers.clear()
    create_barriers()
    create_aliens()

# Create barriers, aliens, and stars
create_barriers()
create_aliens()
create_stars()

# Start alien movement and spaceship movement
move_aliens()
move_spaceship()

# Bind key events to spaceship movement and firing
root.bind("<Left>", start_move_left)
root.bind("<Right>", start_move_right)
root.bind("<KeyRelease-Left>", stop_move)
root.bind("<KeyRelease-Right>", stop_move)
root.bind("<space>", fire_bullet)

# Start alien bomb dropping mechanism
drop_alien_bombs()

root.mainloop()

import random
from pathlib import Path

import pygame
from cards import generate_all_cards


SCREEN_W, SCREEN_H = 800, 600
FPS = 60


def load_background():
	"""Load background_higher_or_lower.png first, then fall back to other casino backgrounds."""
	base_dir = Path(__file__).resolve().parent
	candidates = [
		base_dir / "img" / "background_higher_or_lower.png",
		base_dir.parent / "walk player" / "images" / "lobby_background.png",
		base_dir.parent / "choose player" / "assets" / "backgrounds" / "background_choose_player.png",
	]
	for path in candidates:
		if path.exists():
			try:
				img = pygame.image.load(str(path)).convert()
				return pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
			except Exception:
				continue
	# Fallback to plain color if nothing loads
	surface = pygame.Surface((SCREEN_W, SCREEN_H))
	surface.fill((20, 20, 20))
	return surface


def draw_centered_text(surface, text, font, color, y):
	rendered = font.render(text, True, color)
	rect = rendered.get_rect(center=(SCREEN_W // 2, y))
	surface.blit(rendered, rect)


def draw_flipped_card(screen, card_img, x, y, flip_progress):
	"""
	Draw a card with horizontal flip animation.
	flip_progress: 0.0 = fully showing, 1.0 = edge-on (invisible), 2.0 = fully showing reverse
	"""
	width = card_img.get_width()
	height = card_img.get_height()
	
	# Calculate scaled width based on flip progress (0->1->0)
	if flip_progress <= 1.0:
		scale_x = 1.0 - flip_progress
	else:
		scale_x = flip_progress - 1.0
	
	if scale_x < 0.01:
		scale_x = 0.01  # Prevent zero width
	
	scaled_width = int(width * scale_x)
	scaled_card = pygame.transform.scale(card_img, (scaled_width, height))
	
	# Center the scaled card
	offset_x = (width - scaled_width) // 2
	screen.blit(scaled_card, (x + offset_x, y))


def main():
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
	pygame.display.set_caption("Higher or Lower")
	clock = pygame.time.Clock()

	bg_image = load_background()
	card_images, card_back = generate_all_cards(width=140, height=200)
	info_font = pygame.font.SysFont(None, 36)
	small_font = pygame.font.SysFont(None, 28)

	def draw_game(current, next_val, balance, bet, message, flip_progress=0.0):
		screen.blit(bg_image, (0, 0))

		# Top Center - Balance
		balance_text = info_font.render(f"Balance: ${balance}", True, (255, 215, 0))
		balance_rect = balance_text.get_rect(center=(SCREEN_W // 2, 65))
		screen.blit(balance_text, balance_rect)
		
		# Top Left - Current Bet and buttons
		bet_text = info_font.render(f"Current Bet: ${bet}", True, (255, 255, 255))
		screen.blit(bet_text, (30, 80))
		
		# Bet adjustment buttons
		button_y = 120
		minus_button = pygame.Rect(30, button_y, 40, 40)
		plus_button = pygame.Rect(80, button_y, 40, 40)
		allin_button = pygame.Rect(130, button_y, 80, 40)
		bet50_button = pygame.Rect(30, button_y + 50, 60, 40)
		bet100_button = pygame.Rect(100, button_y + 50, 70, 40)
		
		# Draw buttons
		pygame.draw.rect(screen, (180, 50, 50), minus_button, border_radius=8)
		pygame.draw.rect(screen, (50, 180, 50), plus_button, border_radius=8)
		pygame.draw.rect(screen, (218, 165, 32), allin_button, border_radius=8)  # Gold button
		pygame.draw.rect(screen, (70, 130, 180), bet50_button, border_radius=8)  # Blue button
		pygame.draw.rect(screen, (130, 70, 180), bet100_button, border_radius=8)  # Purple button
		pygame.draw.rect(screen, (255, 255, 255), minus_button, width=2, border_radius=8)
		pygame.draw.rect(screen, (255, 255, 255), plus_button, width=2, border_radius=8)
		pygame.draw.rect(screen, (255, 255, 255), allin_button, width=2, border_radius=8)
		pygame.draw.rect(screen, (255, 255, 255), bet50_button, width=2, border_radius=8)
		pygame.draw.rect(screen, (255, 255, 255), bet100_button, width=2, border_radius=8)
		
		# Button text
		button_font = pygame.font.SysFont(None, 48)
		small_button_font = pygame.font.SysFont(None, 24)
		minus_text = button_font.render("-", True, (255, 255, 255))
		plus_text = button_font.render("+", True, (255, 255, 255))
		allin_text = small_button_font.render("ALL IN", True, (255, 255, 255))
		bet50_text = small_button_font.render("$50", True, (255, 255, 255))
		bet100_text = small_button_font.render("$100", True, (255, 255, 255))
		screen.blit(minus_text, (minus_button.centerx - minus_text.get_width()//2, minus_button.centery - minus_text.get_height()//2))
		screen.blit(plus_text, (plus_button.centerx - plus_text.get_width()//2, plus_button.centery - plus_text.get_height()//2))
		screen.blit(allin_text, (allin_button.centerx - allin_text.get_width()//2, allin_button.centery - allin_text.get_height()//2))
		screen.blit(bet50_text, (bet50_button.centerx - bet50_text.get_width()//2, bet50_button.centery - bet50_text.get_height()//2))
		screen.blit(bet100_text, (bet100_button.centerx - bet100_text.get_width()//2, bet100_button.centery - bet100_text.get_height()//2))
		
		# Bottom HUD - Instructions
		draw_centered_text(screen, "Guess if the next card is HIGHER (arrow ^) or LOWER (arrow v)", small_font, (255, 255, 255), SCREEN_H - 125)
		draw_centered_text(screen, "ESC to quit", small_font, (230, 230, 230), SCREEN_H - 95)

		# Cards layout: LEFT card flips, RIGHT card always visible
		card_w = list(card_images.values())[0].get_width()
		card_h = list(card_images.values())[0].get_height()
		gap = 60
		left_x = SCREEN_W // 2 - card_w - gap // 2
		right_x = SCREEN_W // 2 + gap // 2
		card_y = SCREEN_H // 2 - card_h // 2 - 20

		# Right card - always visible with current value
		if current in card_images:
			screen.blit(card_images[current], (right_x, card_y))

		# Left card - animates flip from back to front
		if flip_progress == 0.0:
			# Show card back (not flipping)
			screen.blit(card_back, (left_x, card_y))
		elif flip_progress >= 2.0:
			# Flip complete - show next card value
			if next_val in card_images:
				screen.blit(card_images[next_val], (left_x, card_y))
		else:
			# Flipping animation in progress
			if flip_progress < 1.0:
				# First half: show card back shrinking
				draw_flipped_card(screen, card_back, left_x, card_y, flip_progress)
			else:
				# Second half: show card front growing
				if next_val in card_images:
					draw_flipped_card(screen, card_images[next_val], left_x, card_y, flip_progress)

		if message:
			draw_centered_text(screen, message, info_font, (255, 255, 0), SCREEN_H - 150)
		
		return minus_button, plus_button, allin_button, bet50_button, bet100_button  # Return button rects for click detection

	def new_round():
		first = random.randint(1, 13)
		second = random.randint(1, 13)
		while second == first:
			second = random.randint(1, 13)
		return first, second

	balance = 1000  # Starting balance
	bet = 50  # Starting bet
	current, next_val = new_round()
	message = ""
	reveal_timer = 0
	reveal_duration_ms = 1500  # 1.5 seconds for flip + reveal
	flip_duration_ms = 600  # 600ms for flip animation
	waiting_reveal = False
	flip_progress = 0.0

	# Button rectangles (will be updated each frame)
	minus_button = pygame.Rect(0, 0, 0, 0)
	plus_button = pygame.Rect(0, 0, 0, 0)
	allin_button = pygame.Rect(0, 0, 0, 0)
	bet50_button = pygame.Rect(0, 0, 0, 0)
	bet100_button = pygame.Rect(0, 0, 0, 0)
	
	running = True
	while running:
		dt = clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				if not waiting_reveal:
					# Guess controls
					if event.key in (pygame.K_UP, pygame.K_DOWN):
						if balance >= bet:
							guess_higher = event.key == pygame.K_UP
							result_higher = next_val > current
							correct = (guess_higher == result_higher)
							if correct:
								balance += bet
								message = f"Correct! Won ${bet}!"
							else:
								balance -= bet
								message = f"Wrong! Lost ${bet}!"
							waiting_reveal = True
							reveal_timer = 0
							flip_progress = 0.0
						else:
							message = "Not enough balance!"
			elif event.type == pygame.MOUSEBUTTONDOWN and not waiting_reveal:
				if event.button == 1:  # Left click
					mouse_pos = event.pos
					if minus_button.collidepoint(mouse_pos):
						if bet > 10:
							bet -= 10
					elif plus_button.collidepoint(mouse_pos):
						if bet + 10 <= balance:
							bet += 10
					elif allin_button.collidepoint(mouse_pos):
						bet = balance
					elif bet50_button.collidepoint(mouse_pos):
						if balance >= 50:
							bet = 50
						else:
							bet = balance
					elif bet100_button.collidepoint(mouse_pos):
						if balance >= 100:
							bet = 100
						else:
							bet = balance

		if waiting_reveal:
			reveal_timer += dt
			
			# Update flip animation
			if reveal_timer < flip_duration_ms:
				# Animate flip: 0 -> 2 over flip_duration
				flip_progress = (reveal_timer / flip_duration_ms) * 2.0
			else:
				flip_progress = 2.0  # Flip complete
			
			if reveal_timer >= reveal_duration_ms:
				# Check if player is bankrupt
				if balance <= 0:
					message = "Game Over! You're out of money!"
					flip_progress = 2.0
				else:
					# Start next round
					current = next_val
					next_val = random.randint(1, 13)
					while next_val == current:
						next_val = random.randint(1, 13)
					waiting_reveal = False
					flip_progress = 0.0
					message = ""
					# Adjust bet if it exceeds balance
					if bet > balance:
						bet = max(10, balance)

		minus_button, plus_button, allin_button, bet50_button, bet100_button = draw_game(current, next_val, balance, bet, message, flip_progress)
		pygame.display.flip()

	pygame.quit()


if __name__ == "__main__":
	main()

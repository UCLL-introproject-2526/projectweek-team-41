"""move.py

This module contains the `Player` class used in the casino lobby scenes.

If you're new to game-dev:
- The player is updated every frame using `player.update(dt, keys, bounds, ...)`.
- `dt` is delta-time (seconds since last frame). Using dt makes movement speed
	consistent even if FPS changes.
- `keys = pygame.key.get_pressed()` returns a boolean-like array for key states
	(held down or not). That is great for continuous movement.

The `Player` here is implemented as a circle for collision math, but drawn as a
sprite image when available.
"""

import pygame
import os
from pathlib import Path
from gifimage import GIFImage


class Player:
	def __init__(
		self,
		pos: tuple[float, float],
		radius: int = 18,
		speed: float = 220.0,
		walk_frame_time: float = 0.12,
	):
		self.x = float(pos[0])
		self.y = float(pos[1])
		self.radius = radius
		self.speed = speed

		self._walk_frame_time = float(walk_frame_time)
		self._walk_timer = 0.0
		self._walk_frame = 0

		self._is_moving = False
		self._facing_right = True  # Track which direction player is facing
		# In sprite-based games it's common to track a "facing direction" so you can
		# flip the sprite when moving left.
		
		# Emote state
		self._emote_active = False
		self._emote_timer = 0.0
		self._emote_duration = 3.0  # seconds
		
		# Dancing state (mirror flip)
		self._is_dancing = False
		self._dance_timer = 0.0
		self._dance_flip_interval = 0.5  # 2 times per second = 0.5s interval
		self._dance_flipped = False
		
		# Load character images
		self._load_images()

	def _load_images(self):
		"""Load character sprite images."""
		# Loading images is usually done once up front (not every frame) for
		# performance. `convert_alpha()` keeps transparency.
		try:
			base_dir = str(Path(__file__).resolve().parent)
		except:
			base_dir = str(Path.cwd())
		
		# Target size for the character.
		# Even though physics uses a circle (`radius`), sprites can be a bit larger.
		target_size = (self.radius * 3, self.radius * 3)
		
		try:
			# Load idle/base character image
			idle_path = os.path.join(base_dir, "assets", "img", "standing.png")
			self._img_idle = pygame.image.load(idle_path).convert_alpha()
			self._img_idle = pygame.transform.smoothscale(self._img_idle, target_size)
		except Exception:
			self._img_idle = None
		
		try:
			# Load left foot walking frame
			left_path = os.path.join(base_dir, "assets", "img", "leftfoot.png")
			self._img_left = pygame.image.load(left_path).convert_alpha()
			self._img_left = pygame.transform.smoothscale(self._img_left, target_size)
		except Exception:
			self._img_left = None
		
		try:
			# Load right foot walking frame
			right_path = os.path.join(base_dir, "assets", "img", "rightfoot.png")
			self._img_right = pygame.image.load(right_path).convert_alpha()
			self._img_right = pygame.transform.smoothscale(self._img_right, target_size)
		except Exception:
			self._img_right = None
		
		# Fallback colors if images don't load
		self._color_idle = (255, 255, 255)
		self._color_walk_0 = (230, 60, 60)   # rood
		self._color_walk_1 = (70, 210, 90)   # groen
		
		# Load smoke gif animation using GIFImage
		try:
			smoke_path = os.path.join(base_dir, "assets", "img", "smoke.gif")
			self._smoke_gif = GIFImage(smoke_path, size=(30, 30))
		except Exception:
			self._smoke_gif = None

	def trigger_emote(self) -> None:
		"""Trigger the smoke emote for 3 seconds."""
		if not self._emote_active and self._smoke_gif:
			self._emote_active = True
			self._emote_timer = 0.0
			self._smoke_gif.reset()

	def set_dancing(self, dancing: bool) -> None:
		"""Set whether the player is on the dancefloor."""
		self._is_dancing = dancing
		if not dancing:
			self._dance_flipped = False
			self._dance_timer = 0.0

	def _get_move_vector_from_keys(self, keys: pygame.key.ScancodeWrapper) -> tuple[float, float]:
		# WASD (QWERTY) + ZQSD (AZERTY) + arrow keys.
		# We support multiple keyboard layouts by checking multiple key constants.
		up = keys[pygame.K_w] or keys[pygame.K_z] or keys[pygame.K_UP]
		down = keys[pygame.K_s] or keys[pygame.K_DOWN]
		left = keys[pygame.K_a] or keys[pygame.K_q] or keys[pygame.K_LEFT]
		right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

		dx = (1 if right else 0) - (1 if left else 0)
		dy = (1 if down else 0) - (1 if up else 0)

		# Diagonal movement would be faster if we just added x and y.
		# So we normalize (scale) diagonal movement by 1/sqrt(2).
		if dx != 0 and dy != 0:
			inv_len = (2.0 ** 0.5) / 2.0  # 1/sqrt(2)
			return dx * inv_len, dy * inv_len

		return float(dx), float(dy)

	def _resolve_circle_rect_collision(self, rect: pygame.Rect) -> None:
		# Collision resolution:
		# Treat the player as a circle and obstacles as rectangles.
		# If the circle overlaps a rect, we push the circle back out.
		closest_x = min(max(self.x, rect.left), rect.right)
		closest_y = min(max(self.y, rect.top), rect.bottom)
		dx = self.x - closest_x
		dy = self.y - closest_y

		r = float(self.radius)
		dist_sq = dx * dx + dy * dy
		if dist_sq >= r * r:
			return

		# Special case: if the circle center is inside the rect (or exactly at a corner)
		# then dx==dy==0. We choose the smallest axis push to get out.
		if dist_sq == 0.0:
			to_left = abs(self.x - rect.left)
			to_right = abs(rect.right - self.x)
			to_top = abs(self.y - rect.top)
			to_bottom = abs(rect.bottom - self.y)
			m = min(to_left, to_right, to_top, to_bottom)
			if m == to_left:
				self.x = rect.left - r
			elif m == to_right:
				self.x = rect.right + r
			elif m == to_top:
				self.y = rect.top - r
			else:
				self.y = rect.bottom + r
			return

		dist = dist_sq ** 0.5
		penetration = r - dist
		nx = dx / dist
		ny = dy / dist
		self.x += nx * penetration
		self.y += ny * penetration

	def update(
		self,
		dt: float,
		keys: pygame.key.ScancodeWrapper,
		bounds: pygame.Rect,
		obstacles: list[pygame.Rect] | None = None,
	) -> None:
		# UPDATE PHASE: update timers/animation state + movement.
		# This method does not draw anything.

		# Update emote timer
		if self._emote_active:
			self._emote_timer += dt
			# Update smoke gif animation
			if self._smoke_gif is not None:
				self._smoke_gif.update(dt)
			# Check if emote duration has passed
			if self._emote_timer >= self._emote_duration:
				self._emote_active = False
		
		# Update dance timer (mirror flip 2 times per second)
		if self._is_dancing:
			self._dance_timer += dt
			if self._dance_timer >= self._dance_flip_interval:
				self._dance_timer -= self._dance_flip_interval
				self._dance_flipped = not self._dance_flipped
		
		dx, dy = self._get_move_vector_from_keys(keys)
		self._is_moving = (dx != 0 or dy != 0)
		
		# Update facing direction based on horizontal movement.
		# This affects sprite flipping in `draw()`.
		if dx > 0:
			self._facing_right = True
		elif dx < 0:
			self._facing_right = False

		# Apply movement using dt so speed is in pixels/second.
		if self._is_moving:
			self.x += dx * self.speed * dt
			self.y += dy * self.speed * dt

			self._walk_timer += dt
			if self._walk_timer >= self._walk_frame_time:
				self._walk_timer -= self._walk_frame_time
				self._walk_frame = 1 - self._walk_frame
		else:
			self._walk_timer = 0.0
			self._walk_frame = 0

		# Collide against obstacles (if any).
		# In this project obstacles are usually empty lists, but the method supports it.
		if obstacles:
			# One pass is enough for simple static obstacles.
			for rect in obstacles:
				self._resolve_circle_rect_collision(rect)

		# Clamp within bounds so you can't walk off-screen.
		# We include the radius so the circle stays fully inside.
		min_x = bounds.left + self.radius
		max_x = bounds.right - self.radius
		min_y = bounds.top + self.radius
		max_y = bounds.bottom - self.radius
		self.x = max(min_x, min(max_x, self.x))
		self.y = max(min_y, min(max_y, self.y))

	def draw(self, surface: pygame.Surface) -> None:
		# DRAW PHASE: render the player.
		# This does not change gameplay state.

		# Select the appropriate image based on movement state
		if not self._is_moving:
			img = self._img_idle
		else:
			img = self._img_left if self._walk_frame == 0 else self._img_right
		
		# Flip sprite based on facing direction (sprites face right by default)
		if img is not None and not self._facing_right:
			img = pygame.transform.flip(img, True, False)
		
		# Apply dance flip if on dancefloor (overrides facing direction)
		if img is not None and self._is_dancing and self._dance_flipped:
			img = pygame.transform.flip(img, True, False)
		
		# Draw image if available, otherwise fall back to colored circle.
		# `blit` copies the sprite pixels onto the destination surface.
		if img is not None:
			# Center the image on the player position
			img_rect = img.get_rect(center=(int(self.x), int(self.y)))
			surface.blit(img, img_rect)
		else:
			# Fallback to circle drawing
			if not self._is_moving:
				color = self._color_idle
			else:
				color = self._color_walk_0 if self._walk_frame == 0 else self._color_walk_1
			pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
		
		# Draw smoke emote if active
		if self._emote_active and self._smoke_gif is not None:
			smoke_frame = self._smoke_gif.get_frame()
			# Position smoke near the character's mouth, mirrored based on facing direction
			if self._facing_right:
				smoke_x = int(self.x) + 30
			else:
				smoke_x = int(self.x) - 30
				smoke_frame = pygame.transform.flip(smoke_frame, True, False)
			smoke_y = int(self.y) - 5
			smoke_rect = smoke_frame.get_rect(center=(smoke_x, smoke_y))
			surface.blit(smoke_frame, smoke_rect)


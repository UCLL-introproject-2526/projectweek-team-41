from __future__ import annotations

import pygame
import os


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
		
		# Emote state
		self._emote_active = False
		self._emote_timer = 0.0
		self._emote_duration = 3.0  # seconds
		self._smoke_frames = []
		self._smoke_frame_index = 0
		self._smoke_frame_timer = 0.0
		self._smoke_frame_delay = 0.1  # seconds per frame
		
		# Load character images
		self._load_images()

	def _load_images(self):
		"""Load character sprite images."""
		base_dir = os.path.dirname(os.path.abspath(__file__))
		
		# Target size for the character (based on radius * 2 for width/height)
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
		
		# Load smoke gif frames for emote
		try:
			smoke_path = os.path.join(base_dir, "assets", "img", "smoke.gif")
			smoke_img = pygame.image.load(smoke_path)
			# For GIF, we try to load multiple frames if PIL is available
			try:
				from PIL import Image 
				pil_img = Image.open(smoke_path)
				self._smoke_frames = []
				try:
					while True:
						frame = pil_img.copy().convert('RGBA')
						frame_data = frame.tobytes()
						pygame_frame = pygame.image.fromstring(frame_data, frame.size, 'RGBA')
						# Scale smoke to appropriate size (about 30x30)
						pygame_frame = pygame.transform.smoothscale(pygame_frame, (30, 30))
						self._smoke_frames.append(pygame_frame)
						pil_img.seek(pil_img.tell() + 1)
				except EOFError:
					pass
			except ImportError:
				# PIL not available, use single frame
				smoke_img = pygame.transform.smoothscale(smoke_img.convert_alpha(), (30, 30))
				self._smoke_frames = [smoke_img]
		except Exception:
			self._smoke_frames = []

	def trigger_emote(self) -> None:
		"""Trigger the smoke emote for 3 seconds."""
		if not self._emote_active and self._smoke_frames:
			self._emote_active = True
			self._emote_timer = 0.0
			self._smoke_frame_index = 0
			self._smoke_frame_timer = 0.0

	def _get_move_vector_from_keys(self, keys: pygame.key.ScancodeWrapper) -> tuple[float, float]:
		# WASD (QWERTY) + ZQSD (AZERTY) + pijltjestoetsen
		up = keys[pygame.K_w] or keys[pygame.K_z] or keys[pygame.K_UP]
		down = keys[pygame.K_s] or keys[pygame.K_DOWN]
		left = keys[pygame.K_a] or keys[pygame.K_q] or keys[pygame.K_LEFT]
		right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

		dx = (1 if right else 0) - (1 if left else 0)
		dy = (1 if down else 0) - (1 if up else 0)

		# Diagonaal toelaten, maar snelheid normaliseren zodat diagonaal niet sneller is.
		if dx != 0 and dy != 0:
			inv_len = (2.0 ** 0.5) / 2.0  # 1/sqrt(2)
			return dx * inv_len, dy * inv_len

		return float(dx), float(dy)

	def _resolve_circle_rect_collision(self, rect: pygame.Rect) -> None:
		# Push the circle out of the rectangle if overlapping.
		closest_x = min(max(self.x, rect.left), rect.right)
		closest_y = min(max(self.y, rect.top), rect.bottom)
		dx = self.x - closest_x
		dy = self.y - closest_y

		r = float(self.radius)
		dist_sq = dx * dx + dy * dy
		if dist_sq >= r * r:
			return

		# If the center is inside the rect (or exactly on an edge corner), choose the
		# smallest axis push to get out.
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
		# Update emote timer
		if self._emote_active:
			self._emote_timer += dt
			self._smoke_frame_timer += dt
			# Animate smoke frames
			if self._smoke_frame_timer >= self._smoke_frame_delay and self._smoke_frames:
				self._smoke_frame_timer -= self._smoke_frame_delay
				self._smoke_frame_index = (self._smoke_frame_index + 1) % len(self._smoke_frames)
			# Check if emote duration has passed
			if self._emote_timer >= self._emote_duration:
				self._emote_active = False
		
		dx, dy = self._get_move_vector_from_keys(keys)
		self._is_moving = (dx != 0 or dy != 0)

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

		if obstacles:
			# One pass is enough for simple static obstacles.
			for rect in obstacles:
				self._resolve_circle_rect_collision(rect)

		# Clamp binnen het scherm (rekening houden met radius)
		min_x = bounds.left + self.radius
		max_x = bounds.right - self.radius
		min_y = bounds.top + self.radius
		max_y = bounds.bottom - self.radius
		self.x = max(min_x, min(max_x, self.x))
		self.y = max(min_y, min(max_y, self.y))

	def draw(self, surface: pygame.Surface) -> None:
		# Select the appropriate image based on movement state
		if not self._is_moving:
			img = self._img_idle
		else:
			img = self._img_left if self._walk_frame == 0 else self._img_right
		
		# Draw image if available, otherwise fall back to colored circle
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
		if self._emote_active and self._smoke_frames:
			smoke_frame = self._smoke_frames[self._smoke_frame_index]
			# Position smoke near the character's mouth (offset to the right and slightly up)
			smoke_x = int(self.x) + 30
			smoke_y = int(self.y) - 5
			smoke_rect = smoke_frame.get_rect(center=(smoke_x, smoke_y))
			surface.blit(smoke_frame, smoke_rect)


from __future__ import annotations

import pygame


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

		self._color_idle = (255, 255, 255)
		self._color_walk_0 = (230, 60, 60)   # rood
		self._color_walk_1 = (70, 210, 90)   # groen

		self._is_moving = False

	def _get_move_vector_from_keys(self, keys: pygame.key.ScancodeWrapper) -> tuple[int, int]:
		# WASD (QWERTY) + ZQSD (AZERTY)
		up = keys[pygame.K_w] or keys[pygame.K_z]
		down = keys[pygame.K_s]
		left = keys[pygame.K_a] or keys[pygame.K_q]
		right = keys[pygame.K_d]

		dx = (1 if right else 0) - (1 if left else 0)
		dy = (1 if down else 0) - (1 if up else 0)

		# Pokémon-achtig: geen diagonaal; kies één as.
		if dx != 0 and dy != 0:
			# Prioriteit: laatste horizontale input winnen voelt meestal OK.
			# Maar zonder input-history: pak horizontaal.
			dy = 0

		return dx, dy

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
		if not self._is_moving:
			color = self._color_idle
		else:
			color = self._color_walk_0 if self._walk_frame == 0 else self._color_walk_1
		pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)


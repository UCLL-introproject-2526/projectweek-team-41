
import pygame


def draw_test_scene(surface: pygame.Surface, font: pygame.font.Font) -> None:
	surface.fill((0, 0, 0))
	text_surf = font.render("Hello world", True, (255, 255, 255))
	text_rect = text_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
	surface.blit(text_surf, text_rect)


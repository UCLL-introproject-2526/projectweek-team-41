"""
GIFImage - A class for loading and animating GIF files in Pygame.
Uses PIL/Pillow to extract frames from animated GIFs.
"""
import pygame
from pathlib import Path

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class GIFImage:
    """A class to load and animate GIF images in Pygame."""
    
    def __init__(self, filepath: str, size: tuple[int, int] | None = None):
        """
        Initialize a GIFImage.
        
        Args:
            filepath: Path to the GIF file
            size: Optional tuple (width, height) to scale the GIF to
        """
        self.filepath = filepath
        self.size = size
        self.frames: list[pygame.Surface] = []
        self.frame_durations: list[float] = []  # Duration in seconds for each frame
        self.current_frame = 0
        self.elapsed_time = 0.0
        self._paused = False
        
        self._load_gif()
    
    def _load_gif(self) -> None:
        """Load all frames from the GIF file with proper transparency handling."""
        if not PIL_AVAILABLE:
            # Fallback: just load the first frame with pygame
            self._load_single_frame()
            return
        
        try:
            gif = Image.open(self.filepath)
            
            # Check if it's animated
            try:
                n_frames = gif.n_frames
            except AttributeError:
                n_frames = 1
            
            # Get the base size and palette info
            base_size = gif.size
            
            # Store all frames properly extracted
            pil_frames = []
            
            # Extract all frames first
            for frame_idx in range(n_frames):
                gif.seek(frame_idx)
                # Copy the frame to preserve it
                pil_frames.append(gif.copy())
            
            # Now process each frame
            # Keep track of the previous frame for proper compositing
            prev_frame = None
            
            for frame_idx, pil_frame in enumerate(pil_frames):
                # Get frame duration
                duration_ms = pil_frame.info.get('duration', 100)
                if duration_ms == 0:
                    duration_ms = 100
                self.frame_durations.append(duration_ms / 1000.0)
                
                # Handle transparency properly
                # Check if frame has transparency
                if 'transparency' in pil_frame.info:
                    # Convert palette image with transparency to RGBA
                    pil_frame = pil_frame.convert('RGBA')
                    
                    # Get the alpha channel and make transparent pixels fully transparent
                    datas = pil_frame.getdata()
                    new_data = []
                    for item in datas:
                        # If pixel is fully transparent or very close to it
                        if item[3] < 10:
                            new_data.append((0, 0, 0, 0))
                        else:
                            new_data.append(item)
                    pil_frame.putdata(new_data)
                else:
                    pil_frame = pil_frame.convert('RGBA')
                
                # Create pygame surface
                data = pil_frame.tobytes()
                surface = pygame.image.fromstring(data, pil_frame.size, 'RGBA')
                surface = surface.convert_alpha()
                
                # Scale if size is specified
                if self.size is not None:
                    surface = pygame.transform.smoothscale(surface, self.size)
                
                self.frames.append(surface)
            
            gif.close()
            
        except Exception as e:
            print(f"Error loading GIF with PIL: {e}")
            self._load_single_frame()
    
    def _load_single_frame(self) -> None:
        """Fallback to load just the first frame using pygame."""
        try:
            surface = pygame.image.load(self.filepath).convert_alpha()
            if self.size is not None:
                surface = pygame.transform.smoothscale(surface, self.size)
            self.frames = [surface]
            self.frame_durations = [0.1]  # Default 100ms
        except Exception as e:
            print(f"Error loading GIF: {e}")
            # Create a placeholder surface
            size = self.size if self.size else (50, 50)
            placeholder = pygame.Surface(size, pygame.SRCALPHA)
            placeholder.fill((255, 0, 255, 128))  # Magenta placeholder
            self.frames = [placeholder]
            self.frame_durations = [0.1]
    
    def update(self, dt: float) -> None:
        """
        Update the animation.
        
        Args:
            dt: Delta time in seconds since last update
        """
        if self._paused or len(self.frames) <= 1:
            return
        
        self.elapsed_time += dt
        
        # Check if we need to advance to the next frame
        while self.elapsed_time >= self.frame_durations[self.current_frame]:
            self.elapsed_time -= self.frame_durations[self.current_frame]
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def get_frame(self) -> pygame.Surface:
        """Get the current frame surface."""
        if not self.frames:
            size = self.size if self.size else (50, 50)
            return pygame.Surface(size, pygame.SRCALPHA)
        return self.frames[self.current_frame]
    
    def draw(self, surface: pygame.Surface, pos: tuple[int, int]) -> None:
        """
        Draw the current frame to a surface.
        
        Args:
            surface: The pygame surface to draw on
            pos: The (x, y) position to draw at
        """
        surface.blit(self.get_frame(), pos)
    
    def pause(self) -> None:
        """Pause the animation."""
        self._paused = True
    
    def resume(self) -> None:
        """Resume the animation."""
        self._paused = False
    
    def reset(self) -> None:
        """Reset the animation to the first frame."""
        self.current_frame = 0
        self.elapsed_time = 0.0
    
    @property
    def is_paused(self) -> bool:
        """Check if the animation is paused."""
        return self._paused
    
    @property
    def frame_count(self) -> int:
        """Get the total number of frames."""
        return len(self.frames)
    
    def get_size(self) -> tuple[int, int]:
        """Get the size of the GIF frames."""
        if self.frames:
            return self.frames[0].get_size()
        return self.size if self.size else (0, 0)

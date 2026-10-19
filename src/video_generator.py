"""
Anjiru.AI Video Generation & Visual Simulation Engine
Procedural 30 FPS MP4 video synthesis with physics, particles, and kinetic typography.
"""

import math
import numpy as np
import cv2
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIDEO_DIR = PROJECT_ROOT / "workspace" / "projects" / "videos"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


class AnjiruVideoGenerator:
    """Renders algorithmic motion videos directly to MP4."""

    def __init__(self, width: int = 640, height: int = 360, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps

    def _render_neural_network_frame(self, frame_idx: int, total_frames: int, prompt: str) -> np.ndarray:
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Deep navy background
        frame[:] = (15, 10, 25)

        t = frame_idx / self.fps
        t_norm = frame_idx / total_frames

        # Layer node layout: Input (3), Hidden 1 (5), Hidden 2 (5), Output (2)
        layers = [3, 5, 5, 2]
        layer_x = np.linspace(80, self.width - 80, len(layers))
        all_nodes = []

        for l_idx, num_nodes in enumerate(layers):
            lx = layer_x[l_idx]
            ly = np.linspace(50, self.height - 70, num_nodes)
            layer_pts = []
            for n_idx, y in enumerate(ly):
                # Gentle vertical floating oscillation
                float_y = y + 4.0 * math.sin(t * 3.0 + l_idx * 1.5 + n_idx)
                layer_pts.append((int(lx), int(float_y)))
            all_nodes.append(layer_pts)

        # Draw synaptic connections with animated pulses
        for l in range(len(all_nodes) - 1):
            curr_layer = all_nodes[l]
            next_layer = all_nodes[l + 1]
            for n1 in curr_layer:
                for n2 in next_layer:
                    # Draw base faint synpatic line
                    cv2.line(frame, n1, n2, (45, 30, 70), 1, cv2.LINE_AA)
                    # Animated firing pulse traveling down synapse
                    pulse_progress = (t * 2.5 + (n1[0] + n1[1] + n2[1]) * 0.01) % 1.0
                    px = int(n1[0] + pulse_progress * (n2[0] - n1[0]))
                    py = int(n1[1] + pulse_progress * (n2[1] - n1[1]))
                    cv2.circle(frame, (px, py), 2, (180, 240, 70), -1, cv2.LINE_AA)

        # Draw glowing nodes
        for l_idx, layer in enumerate(all_nodes):
            for pt in layer:
                # Outer glow
                cv2.circle(frame, pt, 8, (60, 40, 110), -1, cv2.LINE_AA)
                # Core node (Cyan/Emerald)
                color = (230, 180, 16) if l_idx == len(all_nodes) - 1 else (160, 230, 30)
                cv2.circle(frame, pt, 4, color, -1, cv2.LINE_AA)

        # Header Title
        title_text = f"Anjiru.AI Neural Network | {prompt[:28]}"
        cv2.putText(frame, title_text, (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)
        
        # Subtitle & Status
        sub_text = f"FPS: {self.fps} | Frame: {frame_idx:03d}/{total_frames} | Synaptic Flow: Active"
        cv2.putText(frame, sub_text, (20, self.height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 180, 120), 1, cv2.LINE_AA)

        # Progress bar at bottom
        bar_w = int(self.width * t_norm)
        cv2.rectangle(frame, (0, self.height - 4), (bar_w, self.height), (16, 185, 129), -1)

        return frame

    def _render_kinetic_typography_frame(self, frame_idx: int, total_frames: int, prompt: str) -> np.ndarray:
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Gradient background
        t = frame_idx / self.fps
        t_norm = frame_idx / total_frames

        # Animated subtle grid
        grid_offset = int((t * 20) % 30)
        for x in range(grid_offset, self.width, 30):
            cv2.line(frame, (x, 0), (x, self.height), (20, 24, 32), 1)
        for y in range(grid_offset, self.height, 30):
            cv2.line(frame, (0, y), (self.width, y), (20, 24, 32), 1)

        # Pulsing center glow circle
        center_x, center_y = self.width // 2, self.height // 2 - 10
        glow_radius = int(80 + 15 * math.sin(t * 4.0))
        cv2.circle(frame, (center_x, center_y), glow_radius, (35, 20, 50), -1, cv2.LINE_AA)

        # Floating ambient energy particles
        np.random.seed(42)
        particle_seeds = np.random.rand(40, 2)
        for p in particle_seeds:
            px = int((p[0] * self.width + t * 40.0 * (p[1] + 0.2)) % self.width)
            py = int((p[1] * self.height + math.sin(t * 2.0 + p[0] * 10) * 20) % self.height)
            cv2.circle(frame, (px, py), 2, (120, 200, 255), -1, cv2.LINE_AA)

        # Render Main Title
        brand_text = "ANJIRU.AI SYNTHESIS"
        cv2.putText(frame, brand_text, (center_x - 130, center_y - 35), cv2.FONT_HERSHEY_DUPLEX, 0.65, (16, 185, 129), 1, cv2.LINE_AA)

        # Main prompt text with drop shadow
        display_prompt = prompt.upper()[:32]
        text_size = cv2.getTextSize(display_prompt, cv2.FONT_HERSHEY_DUPLEX, 0.75, 2)[0]
        tx = max(20, center_x - text_size[0] // 2)
        # Shadow
        cv2.putText(frame, display_prompt, (tx + 2, center_y + 12), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
        # Core
        cv2.putText(frame, display_prompt, (tx, center_y + 10), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        # Subtitle tag
        tag_text = "SOVEREIGN KENYAN INTELLIGENCE | HIGH DENSITY EXECUTION"
        tag_size = cv2.getTextSize(tag_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)[0]
        cv2.putText(frame, tag_text, (center_x - tag_size[0] // 2, center_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (148, 163, 184), 1, cv2.LINE_AA)

        # Animated bracket frames
        corner_len = 25
        # Top-left
        cv2.line(frame, (40, 40), (40 + corner_len, 40), (16, 185, 129), 2)
        cv2.line(frame, (40, 40), (40, 40 + corner_len), (16, 185, 129), 2)
        # Top-right
        cv2.line(frame, (self.width - 40, 40), (self.width - 40 - corner_len, 40), (16, 185, 129), 2)
        cv2.line(frame, (self.width - 40, 40), (self.width - 40, 40 + corner_len), (16, 185, 129), 2)
        # Bottom-left
        cv2.line(frame, (40, self.height - 40), (40 + corner_len, self.height - 40), (16, 185, 129), 2)
        cv2.line(frame, (40, self.height - 40), (40, self.height - 40 - corner_len), (16, 185, 129), 2)
        # Bottom-right
        cv2.line(frame, (self.width - 40, self.height - 40), (self.width - 40 - corner_len, self.height - 40), (16, 185, 129), 2)
        cv2.line(frame, (self.width - 40, self.height - 40), (self.width - 40, self.height - 40 - corner_len), (16, 185, 129), 2)

        # Timeline bar
        bar_w = int(self.width * t_norm)
        cv2.rectangle(frame, (0, self.height - 4), (bar_w, self.height), (99, 102, 241), -1)

        return frame

    def _render_orbital_gravity_frame(self, frame_idx: int, total_frames: int, prompt: str) -> np.ndarray:
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = (8, 6, 14)

        t = frame_idx / self.fps
        center_x, center_y = self.width // 2, self.height // 2

        # Central Sun/Attractor
        cv2.circle(frame, (center_x, center_y), 24, (20, 60, 180), -1, cv2.LINE_AA)
        cv2.circle(frame, (center_x, center_y), 14, (30, 150, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, (center_x, center_y), 8, (220, 240, 255), -1, cv2.LINE_AA)

        # 3 Planets with distinct Keplerian orbits
        planets = [
            {"radius_x": 75, "radius_y": 45, "speed": 1.8, "color": (80, 220, 120), "size": 6, "name": "Mercury"},
            {"radius_x": 135, "radius_y": 80, "speed": 1.1, "color": (220, 150, 50), "size": 9, "name": "Earth"},
            {"radius_x": 210, "radius_y": 125, "speed": 0.65, "color": (100, 140, 240), "size": 12, "name": "Jupiter"}
        ]

        for p in planets:
            # Draw faint orbit ellipse
            cv2.ellipse(frame, (center_x, center_y), (p["radius_x"], p["radius_y"]), 0, 0, 360, (30, 25, 45), 1, cv2.LINE_AA)
            
            # Position
            angle = t * p["speed"]
            px = int(center_x + p["radius_x"] * math.cos(angle))
            py = int(center_y + p["radius_y"] * math.sin(angle))

            # Gravity vector line
            cv2.line(frame, (center_x, center_y), (px, py), (35, 30, 55), 1, cv2.LINE_AA)

            # Planet Body
            cv2.circle(frame, (px, py), p["size"] + 3, (p["color"][0]//3, p["color"][1]//3, p["color"][2]//3), -1, cv2.LINE_AA)
            cv2.circle(frame, (px, py), p["size"], p["color"], -1, cv2.LINE_AA)

        # Title
        cv2.putText(frame, f"Keplerian Gravitational Simulator: {prompt[:24]}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Central Mass M=1.989e30 kg | G=6.674e-11 | Step: {frame_idx}", (20, self.height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (140, 160, 140), 1, cv2.LINE_AA)

        t_norm = frame_idx / total_frames
        cv2.rectangle(frame, (0, self.height - 4), (int(self.width * t_norm), self.height), (59, 130, 246), -1)

        return frame

    def generate_video(self, prompt: str, duration_sec: float = 3.0, style: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesizes procedural MP4 video from description.
        Styles: neural_network, kinetic_typography, orbital_gravity.
        """
        clean_prompt = prompt.strip()
        lower_p = clean_prompt.lower()

        if not style:
            if any(w in lower_p for w in ["neural", "brain", "ai", "network", "synapse", "model"]):
                style = "neural_network"
            elif any(w in lower_p for w in ["orbit", "gravity", "planet", "physics", "solar", "space"]):
                style = "orbital_gravity"
            else:
                style = "kinetic_typography"

        total_frames = int(self.fps * duration_sec)
        slug = "".join(c if c.isalnum() else "_" for c in clean_prompt[:20]).strip("_").lower() or "simulation"
        filename = f"anjiru_{style}_{slug}.mp4"
        output_path = VIDEO_DIR / filename

        # Video writer using mp4v
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, float(self.fps), (self.width, self.height))

        for idx in range(total_frames):
            if style == "neural_network":
                frame = self._render_neural_network_frame(idx, total_frames, clean_prompt)
            elif style == "orbital_gravity":
                frame = self._render_orbital_gravity_frame(idx, total_frames, clean_prompt)
            else:
                frame = self._render_kinetic_typography_frame(idx, total_frames, clean_prompt)
            out.write(frame)

        out.release()

        file_size = os.path.getsize(str(output_path))

        return {
            "status": "success",
            "prompt": clean_prompt,
            "style": style,
            "duration_sec": duration_sec,
            "fps": self.fps,
            "resolution": f"{self.width}x{self.height}",
            "total_frames": total_frames,
            "file_name": filename,
            "file_path": str(output_path),
            "url": f"/api/video/download?file={filename}",
            "size_bytes": file_size
        }


# Global singleton
_video_generator = None

def get_video_generator() -> AnjiruVideoGenerator:
    global _video_generator
    if _video_generator is None:
        _video_generator = AnjiruVideoGenerator()
    return _video_generator

import moderngl
import numpy as np
from freetype import Face
from moderngl_window import WindowConfig, run_window_config


class TextRenderer:
    def __init__(self, ctx, font_path, font_size=48):
        self.ctx = ctx
        self.font_size = font_size
        self.face = Face(font_path)
        self.face.set_char_size(font_size * 64)

        # Generate a white texture for rendering text (glyphs will be added here)
        self.atlas_texture = self.ctx.texture((512, 512), components=1, dtype="f1")
        self.atlas_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Create a buffer to hold vertex positions and texture coordinates
        self.vbo = self.ctx.buffer(
            reserve=4 * 4 * 6
        )  # 6 vertices per quad (2 triangles)
        self.vao = None

        self._setup_shader()

    def _setup_shader(self):
        vertex_shader = """
        #version 330
        in vec2 in_vert;
        in vec2 in_text;
        out vec2 v_text;
        uniform vec2 screen_size;
        void main() {
            v_text = in_text;
            gl_Position = vec4(in_vert / screen_size * 2.0 - 1.0, 0.0, 1.0);
        }
        """
        fragment_shader = """
        #version 330
        in vec2 v_text;
        out vec4 fragColor;
        uniform sampler2D text_texture;

        void main() {
            float alpha = texture(text_texture, v_text).r;
            fragColor = vec4(1.0, 1.0, 1.0, alpha);  // White color with alpha from texture
        }
        """
        self.text_shader = self.ctx.program(
            vertex_shader=vertex_shader, fragment_shader=fragment_shader
        )

    def render_text(self, position, text):
        x, y = position

        # Activate the texture
        self.atlas_texture.use()

        vertices = []
        for char in text:
            self.face.load_char(char)

            # Get glyph metrics
            glyph = self.face.glyph
            bitmap = glyph.bitmap

            # Texture coordinates
            w = bitmap.width
            h = bitmap.rows
            left = glyph.bitmap_left
            top = glyph.bitmap_top

            # Calculate vertices for this character
            xpos = x + left
            ypos = y - top
            w = bitmap.width
            h = bitmap.rows

            # Texture coordinates for each quad
            quad_vertices = [
                xpos,
                ypos + h,
                0.0,
                1.0,
                xpos,
                ypos,
                0.0,
                0.0,
                xpos + w,
                ypos,
                1.0,
                0.0,
                xpos,
                ypos + h,
                0.0,
                1.0,
                xpos + w,
                ypos,
                1.0,
                0.0,
                xpos + w,
                ypos + h,
                1.0,
                1.0,
            ]
            vertices.extend(quad_vertices)

            # Advance cursor to the next character
            x += glyph.advance.x >> 6  # Move in 1/64th pixel space

        # Create buffer and render text
        vertices = np.array(vertices, dtype="f4")
        self.vbo.write(vertices)
        self.vao = self.ctx.simple_vertex_array(
            self.text_shader, self.vbo, "in_vert", "in_text"
        )

        # Render the VAO
        self.vao.render(moderngl.TRIANGLES)


class Example(WindowConfig):
    window_size = (800, 600)
    aspect_ratio = 16 / 9
    title = "ModernGL Window with Text Rendering"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx: moderngl.Context = self.wnd.ctx  # ModernGL context

        # Set up the text renderer with a font file
        self.text_renderer = TextRenderer(
            self.ctx,
            font_path="./assets/fira_code/FiraCodeNerdFont-SemiBold.ttf",
            font_size=48,
        )

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.2, 0.3, 0.3)  # Clear screen with a color

        # Call text renderer to render the text at position (100, 100)
        self.text_renderer.render_text((100, 100), "Hello, World!")


if __name__ == "__main__":
    run_window_config(Example)

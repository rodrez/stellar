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

        self.atlas_texture = self.ctx.texture((1024, 1024), components=1, dtype="f1")
        self.atlas_texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.atlas_data = np.zeros((1024, 1024), dtype=np.uint8)
        self.atlas_x, self.atlas_y = 0, 0
        self.atlas_line_height = 0

        self.vbo = self.ctx.buffer(reserve=1024 * 1024)  # Reserve 1MB of buffer space
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
        self.vao = self.ctx.vertex_array(
            self.text_shader,
            [
                (self.vbo, "2f 2f", "in_vert", "in_text"),
            ],
        )

    def _add_glyph_to_atlas(self, bitmap):
        if self.atlas_x + bitmap.width > 1024:
            self.atlas_x = 0
            self.atlas_y += self.atlas_line_height
            self.atlas_line_height = 0

        if self.atlas_y + bitmap.rows > 1024:
            print("Warning: Texture atlas full")
            return None

        x, y = self.atlas_x, self.atlas_y
        self.atlas_data[y : y + bitmap.rows, x : x + bitmap.width] = np.array(
            bitmap.buffer
        ).reshape(bitmap.rows, bitmap.width)

        self.atlas_x += bitmap.width
        self.atlas_line_height = max(self.atlas_line_height, bitmap.rows)

        return x, y, bitmap.width, bitmap.rows

    def render_text(self, position, text):
        x, y = position
        print(f"Rendering text at position: ({x}, {y})")

        vertices = []
        for char in text:
            self.face.load_char(char)
            glyph = self.face.glyph
            bitmap = glyph.bitmap
            print(f"Character '{char}': width={bitmap.width}, rows={bitmap.rows}")

            atlas_pos = self._add_glyph_to_atlas(bitmap)
            if atlas_pos is None:
                continue

            ax, ay, aw, ah = atlas_pos
            left = glyph.bitmap_left
            top = glyph.bitmap_top
            w = bitmap.width
            h = bitmap.rows

            xpos = x + left
            ypos = y - top

            x1 = xpos
            x2 = xpos + w
            y1 = ypos
            y2 = ypos + h

            tex_x1 = ax / 1024
            tex_x2 = (ax + aw) / 1024
            tex_y1 = ay / 1024
            tex_y2 = (ay + ah) / 1024

            quad_vertices = [
                x1,
                y1,
                tex_x1,
                tex_y2,
                x1,
                y2,
                tex_x1,
                tex_y1,
                x2,
                y1,
                tex_x2,
                tex_y2,
                x1,
                y2,
                tex_x1,
                tex_y1,
                x2,
                y1,
                tex_x2,
                tex_y2,
                x2,
                y2,
                tex_x2,
                tex_y1,
            ]
            vertices.extend(quad_vertices)

            x += glyph.advance.x >> 6

        vertices = np.array(vertices, dtype="f4")
        self.vbo.write(vertices)
        self.atlas_texture.write(self.atlas_data)

        self.atlas_texture.use(0)
        self.text_shader["text_texture"] = 0
        self.text_shader["screen_size"] = self.ctx.screen.size
        self.vao.render(moderngl.TRIANGLES, vertices=len(vertices) // 4)

        print(f"Total vertices: {len(vertices)}")


class Example(WindowConfig):
    window_size = (800, 600)
    aspect_ratio = 16 / 9
    title = "ModernGL Window with Text Rendering"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.text_renderer = TextRenderer(
            self.ctx,
            font_path="./assets/fira_code/FiraCodeNerdFont-SemiBold.ttf",
            font_size=48,
        )

    def render(self, time: float, frame_time: float):
        try:
            self.ctx.viewport = (0, 0, self.window_size[0], self.window_size[1])
            self.ctx.clear(0.2, 0.3, 0.3)
            self.text_renderer.render_text((100, 100), "Hello, World!")
        except Exception as e:
            print(f"Error during rendering: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    run_window_config(Example)

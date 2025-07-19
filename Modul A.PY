import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import sys

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def copy(self):
        # Buat salinan point baru (menghindari reference masalah)
        return Point(self.x, self.y)

class Shape:
    def __init__(self, shape_type, points, color=(1.0, 1.0, 1.0), thickness=2):
        self.shape_type = shape_type  # 'titik', 'garis', 'persegi', 'ellipse'
        self.points = [p.copy() for p in points]  # Points asli (backup)
        self.transformed_points = [p.copy() for p in points]  # Points untuk transformasi (yang berubah-ubah)
        self.color = color
        self.thickness = thickness

class OpenGL2DModulA:
    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 800
        
        # Setup pygame dan OpenGL - standar initialization
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("MODUL A: Objek 2D - OpenGL Canvas (Draggable Window)")
        
        # Setup sistem koordinat OpenGL (penting!)
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, self.height, 0)  # Koordinat screen (0,0 kiri atas)  # A.2) INPUT KOORDINAT VIA MOUSE
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Enable anti-aliasing biar garis halus (quality improvement)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        # Variable state program
        self.shapes = []  # List semua objek yang sudah dibuat
        self.current_tool = 'titik'  # Tool yang aktif sekarang
        self.current_color = (1.0, 1.0, 1.0)  # Warna default putih
        self.current_thickness = 3
        self.current_point_size = 12  # BARU: Ukuran titik yang bisa diatur
        self.temp_points = []  # Points sementara saat membuat objek
        self.selected_shape_index = -1  # Index objek yang dipilih (-1 = tidak ada)
        
        # State untuk clipping window
        self.clipping_window = None  # Tuple (point1, point2) atau None         # D.6) WINDOW AKTIF DEFINITION
        self.defining_window = False  # Sedang dalam mode buat window?
        self.window_temp_points = []  # Points sementara untuk window
        
        # BARU: State untuk dragging window clipping
        self.dragging_window = False  # Sedang drag window?
        self.drag_offset_x = 0  # Offset mouse dari corner window saat mulai drag
        self.drag_offset_y = 0
        self.window_hover = False  # Mouse hover di atas window?
        
        # Kontrol transformasi kontinyu (smooth movement)
        self.keys_pressed = set()  # Set tombol yang sedang ditekan
        self.transform_speed = {
            'translate': 3,  # Pixel per frame
            'rotate': 2,     # Derajat per frame
            'scale': 0.02    # Scale factor per frame
        }
        
        # Dictionary warna untuk mudah switch
        self.colors = {                                                        # B.3.a) WARNA OBJEK VIA KEYBOARD
            'merah': (1.0, 0.0, 0.0),
            'hijau': (0.0, 1.0, 0.0),
            'biru': (0.0, 0.0, 1.0),
            'putih': (1.0, 1.0, 1.0),
            'kuning': (1.0, 1.0, 0.0),
            'cyan': (0.0, 1.0, 1.0),
            'magenta': (1.0, 0.0, 1.0)
        }
        
        self.running = True

    def screen_to_opengl(self, screen_x, screen_y):
        """Convert koordinat pygame ke OpenGL (di sini sama karena setup ortho2D)"""
        return screen_x, screen_y

    # BARU: Fungsi untuk mengatur ukuran titik
    def adjust_point_size(self, delta):
        """Ubah ukuran titik dengan batas min/max"""
        self.current_point_size = max(3, min(50, self.current_point_size + delta))
        print(f"📍 Ukuran titik: {self.current_point_size}")

    # BARU: Fungsi untuk drag window clipping
    def is_mouse_on_window(self, mouse_x, mouse_y):
        """Cek apakah mouse berada di atas window clipping (untuk drag detection)"""
        if not self.clipping_window:
            return False
            
        p1, p2 = self.clipping_window
        min_x, max_x = min(p1.x, p2.x), max(p1.x, p2.x)
        min_y, max_y = min(p1.y, p2.y), max(p1.y, p2.y)
        
        # Cek apakah mouse di border window (toleransi 10 pixel untuk mudah klik)
        border_tolerance = 10
        
        # Cek border kiri/kanan
        if (abs(mouse_x - min_x) <= border_tolerance or abs(mouse_x - max_x) <= border_tolerance) and min_y <= mouse_y <= max_y:
            return True
        # Cek border atas/bawah  
        if (abs(mouse_y - min_y) <= border_tolerance or abs(mouse_y - max_y) <= border_tolerance) and min_x <= mouse_x <= max_x:
            return True
        # Cek area dalam window (untuk drag seluruh window)
        if min_x <= mouse_x <= max_x and min_y <= mouse_y <= max_y:
            return True
            
        return False

    def start_window_drag(self, mouse_x, mouse_y):
        """Mulai drag window clipping"""
        if not self.clipping_window:
            return False
            
        if self.is_mouse_on_window(mouse_x, mouse_y):
            self.dragging_window = True
            # Simpan offset dari corner kiri atas window
            p1, p2 = self.clipping_window
            min_x = min(p1.x, p2.x)
            min_y = min(p1.y, p2.y)
            self.drag_offset_x = mouse_x - min_x
            self.drag_offset_y = mouse_y - min_y
            print("🖱️ Mulai drag window clipping...")
            return True
        return False

    def update_window_drag(self, mouse_x, mouse_y):
        """Update posisi window saat drag"""
        if not self.dragging_window or not self.clipping_window:
            return
            
        p1, p2 = self.clipping_window
        
        # Hitung ukuran window
        width = abs(p2.x - p1.x)
        height = abs(p2.y - p1.y)
        
        # Hitung posisi baru berdasarkan offset
        new_min_x = mouse_x - self.drag_offset_x
        new_min_y = mouse_y - self.drag_offset_y
        new_max_x = new_min_x + width
        new_max_y = new_min_y + height
        
        # Batas supaya window tidak keluar dari screen
        if new_min_x < 0:
            new_min_x = 0
            new_max_x = width
        if new_min_y < 0:
            new_min_y = 0
            new_max_y = height
        if new_max_x > self.width:
            new_max_x = self.width
            new_min_x = self.width - width
        if new_max_y > self.height:
            new_max_y = self.height
            new_min_y = self.height - height
            
        # Update window position
        self.clipping_window = (Point(new_min_x, new_min_y), Point(new_max_x, new_max_y))

    def stop_window_drag(self):
        """Stop drag window clipping"""
        if self.dragging_window:
            self.dragging_window = False
            print("🖱️ Stop drag window clipping")

    # ========== A. FUNGSI PENGGAMBARAN OBJEK ==========
    
    def draw_titik(self, point, color, size=None):                             # A.1.a) GAMBAR TITIK
        """A.1.a) Menggambar Titik - pakai filled circle biar keliatan bagus"""
        if size is None:
            size = self.current_point_size
            
        glColor3f(*color)
        
        # Gambar lingkaran penuh pakai GL_TRIANGLE_FAN (smooth circle)
        radius = size
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(point.x, point.y)  # Center point
        for i in range(25):  # 24 segmen + 1 untuk nutup
            angle = 2 * math.pi * i / 24
            x = point.x + radius * math.cos(angle)
            y = point.y + radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
        
        # Tambahin border hitam biar keliatan (visual improvement)
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        for i in range(24):
            angle = 2 * math.pi * i / 24
            x = point.x + radius * math.cos(angle)
            y = point.y + radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()

    def draw_garis(self, p1, p2, color, thickness):                            # A.1.b) GAMBAR GARIS
        """A.1.b) Menggambar Garis - paling simple pakai GL_LINES"""
        glColor3f(*color)
        glLineWidth(thickness)                                                 # B.3.b) KETEBALAN GARIS GL_LINES
        glBegin(GL_LINES)
        glVertex2f(p1.x, p1.y)
        glVertex2f(p2.x, p2.y)
        glEnd()

    def draw_persegi(self, p1, p2, color, thickness):                          # A.1.c) GAMBAR PERSEGI
        """A.1.c) Menggambar Persegi - pakai GL_LINE_LOOP biar otomatis nutup"""
        glColor3f(*color)
        glLineWidth(thickness)                                                 # B.3.b) KETEBALAN GARIS GL_LINE_LOOP
        glBegin(GL_LINE_LOOP)  # LINE_LOOP otomatis connect titik terakhir ke pertama
        glVertex2f(p1.x, p1.y)     # Kiri atas
        glVertex2f(p2.x, p1.y)     # Kanan atas
        glVertex2f(p2.x, p2.y)     # Kanan bawah
        glVertex2f(p1.x, p2.y)     # Kiri bawah
        glEnd()

    def draw_ellipse(self, center, width, height, color, thickness):           # A.1.d) GAMBAR ELLIPSE
        """A.1.d) Menggambar Ellipse - pakai rumus matematika lingkaran"""
        glColor3f(*color)
        glLineWidth(thickness)
        glBegin(GL_LINE_LOOP)
        segments = 50  # Makin banyak segment makin smooth
        for i in range(segments):
            angle = 2 * math.pi * i / segments  # Sudut dari 0 sampai 2π
            # Rumus ellipse: x = center_x + (width/2) * cos(θ)
            #                y = center_y + (height/2) * sin(θ)
            x = center.x + (width / 2) * math.cos(angle)
            y = center.y + (height / 2) * math.sin(angle)
            glVertex2f(x, y)
        glEnd()

    # ========== B. FUNGSI WARNA & KETEBALAN ==========
    
    def set_color_by_name(self, color_name):                                   # B.3.a) PILIH WARNA VIA KEYBOARD
        """B.3.a) Switch warna pakai nama - lebih user friendly"""
        if color_name in self.colors:
            self.current_color = self.colors[color_name]
            print(f"🎨 Warna diubah ke: {color_name.upper()}")
            return True
        return False

    def adjust_thickness(self, delta):                                         # B.3.b) KETEBALAN GARIS
        """B.3.b) Ubah ketebalan dengan batas min/max - prevent error"""
        self.current_thickness = max(1, min(15, self.current_thickness - delta))
        print(f"📏 Ketebalan: {self.current_thickness}")

    # ========== C. TRANSFORMASI GEOMETRI ==========
    
    def apply_translasi(self, shape, dx, dy):                                  # C.4.a) TRANSFORMASI TRANSLASI
        """C.4.a) Translasi - geser semua point dengan offset yang sama"""
        for point in shape.transformed_points:
            point.x += dx  # Geser x
            point.y += dy  # Geser y

    def apply_rotasi(self, shape, angle_degrees):                              # C.4.b) TRANSFORMASI ROTASI
        """C.4.b) Rotasi - putar objek mengelilingi center-nya sendiri"""
        if not shape.transformed_points:
            return
        
        # Hitung center objek (rata-rata semua point)
        center_x = sum(p.x for p in shape.transformed_points) / len(shape.transformed_points)
        center_y = sum(p.y for p in shape.transformed_points) / len(shape.transformed_points)
        
        # Convert derajat ke radian (OpenGL pakai radian)
        angle_rad = math.radians(angle_degrees)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        for point in shape.transformed_points:
            # Pindah ke origin (0,0) dulu
            x = point.x - center_x
            y = point.y - center_y
            
            # Apply rotation matrix: [cos -sin] [x]
            #                        [sin  cos] [y]
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            
            # Pindah balik ke posisi asli
            point.x = new_x + center_x
            point.y = new_y + center_y

    def apply_scaling(self, shape, scale_factor):                              # C.4.c) TRANSFORMASI SCALING
        """C.4.c) Scaling - besarkan/kecilkan dari center objek"""
        if not shape.transformed_points:
            return
        
        # Hitung center objek
        center_x = sum(p.x for p in shape.transformed_points) / len(shape.transformed_points)
        center_y = sum(p.y for p in shape.transformed_points) / len(shape.transformed_points)
        
        for point in shape.transformed_points:
            # Scale dari center: new_point = center + (old_point - center) * scale
            point.x = center_x + (point.x - center_x) * scale_factor
            point.y = center_y + (point.y - center_y) * scale_factor

    # ========== D. WINDOWING DAN CLIPPING ==========
    
    def define_clipping_window(self, p1, p2):                                  # D.6) DEFINISI WINDOW CLIPPING
        """D.6) Definisi window clipping dari 2 titik sudut"""
        self.clipping_window = (p1.copy(), p2.copy())
        print("🪟 Window clipping berhasil didefinisikan")

    def draw_clipping_window(self):
        """Gambar window clipping dengan border dan visual feedback untuk drag"""
        if self.clipping_window:
            p1, p2 = self.clipping_window
            
            # Warna berubah saat hover atau drag
            if self.dragging_window:
                glColor3f(1.0, 0.5, 0.0)  # Orange saat drag
                line_width = 6
            elif self.window_hover:
                glColor3f(1.0, 0.8, 0.0)  # Kuning saat hover
                line_width = 5
            else:
                glColor3f(1.0, 0.0, 0.0)  # Merah normal
                line_width = 4
                
            glLineWidth(line_width)
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1.x, p1.y)
            glVertex2f(p2.x, p1.y)
            glVertex2f(p2.x, p2.y)
            glVertex2f(p1.x, p2.y)
            glEnd()
            
            # Tambahin marker di pojok biar jelas (dan berubah ukuran saat hover/drag)
            if self.dragging_window:
                corner_size = 12
                glColor3f(1.0, 1.0, 0.0)  # Kuning saat drag
            elif self.window_hover:
                corner_size = 10
                glColor3f(0.0, 1.0, 1.0)  # Cyan saat hover
            else:
                corner_size = 8
                glColor3f(1.0, 0.0, 0.0)  # Merah normal
                
            corners = [(p1.x, p1.y), (p2.x, p1.y), (p2.x, p2.y), (p1.x, p2.y)]
            for cx, cy in corners:
                glBegin(GL_QUADS)
                glVertex2f(cx - corner_size, cy - corner_size)
                glVertex2f(cx + corner_size, cy - corner_size)
                glVertex2f(cx + corner_size, cy + corner_size)
                glVertex2f(cx - corner_size, cy + corner_size)
                glEnd()
                
            # BARU: Tambahin text indicator untuk drag (visual hint)
            if self.window_hover and not self.dragging_window:
                # Gambar simbol drag di tengah window
                center_x = (p1.x + p2.x) / 2
                center_y = (p1.y + p2.y) / 2
                glColor3f(1.0, 1.0, 1.0)  # Putih
                
                # Gambar cross untuk indicate draggable
                cross_size = 15
                glLineWidth(3)
                glBegin(GL_LINES)
                # Horizontal line
                glVertex2f(center_x - cross_size, center_y)
                glVertex2f(center_x + cross_size, center_y)
                # Vertical line
                glVertex2f(center_x, center_y - cross_size)
                glVertex2f(center_x, center_y + cross_size)
                glEnd()

    def point_inside_window(self, point):
        """Cek apakah point ada di dalam window"""
        if not self.clipping_window:
            return False
        p1, p2 = self.clipping_window
        # Cari min/max koordinat window (case user klik dari kanan ke kiri)
        min_x, max_x = min(p1.x, p2.x), max(p1.x, p2.x)
        min_y, max_y = min(p1.y, p2.y), max(p1.y, p2.y)
        return min_x <= point.x <= max_x and min_y <= point.y <= max_y

    def cohen_sutherland_line_clipping(self, p1, p2):                          # D.7.b) ALGORITMA COHEN-SUTHERLAND
        """D.7.b) Cohen-Sutherland algorithm - ALGORITMA CLIPPING GARIS ADVANCED!"""
        if not self.clipping_window:
            return p1, p2, True
        
        win_p1, win_p2 = self.clipping_window
        x_min, x_max = min(win_p1.x, win_p2.x), max(win_p1.x, win_p2.x)
        y_min, y_max = min(win_p1.y, win_p2.y), max(win_p1.y, win_p2.y)
        
        def compute_outcode(point):
            """Hitung outcode 4-bit untuk point
            Bit 0: Left, Bit 1: Right, Bit 2: Bottom, Bit 3: Top"""
            code = 0
            if point.x < x_min: code |= 1    # Left
            if point.x > x_max: code |= 2    # Right
            if point.y < y_min: code |= 4    # Bottom
            if point.y > y_max: code |= 8    # Top
            return code
        
        # Kerja dengan copy supaya tidak mengubah original
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        
        outcode1 = compute_outcode(Point(x1, y1))
        outcode2 = compute_outcode(Point(x2, y2))
        
        while True:
            # Case 1: Kedua point di dalam window (outcode = 0000)
            if outcode1 == 0 and outcode2 == 0:
                return Point(x1, y1), Point(x2, y2), True
            
            # Case 2: Kedua point di luar window di sisi yang sama (AND != 0)
            if outcode1 & outcode2 != 0:
                return None, None, False  # Line completely outside
            
            # Case 3: Line perlu di-clip, cari intersection
            if outcode1 != 0:
                outcode_out = outcode1
            else:
                outcode_out = outcode2
            
            # Hitung intersection point berdasarkan outcode
            if outcode_out & 8:  # Top edge
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif outcode_out & 4:  # Bottom edge
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif outcode_out & 2:  # Right edge
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif outcode_out & 1:  # Left edge
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min
            
            # Update point dan outcode, lanjut iterasi
            if outcode_out == outcode1:
                x1, y1 = x, y
                outcode1 = compute_outcode(Point(x1, y1))
            else:
                x2, y2 = x, y
                outcode2 = compute_outcode(Point(x2, y2))

    def enable_opengl_clipping(self):
        """Enable OpenGL hardware clipping - lebih efficient daripada manual"""
        if not self.clipping_window:
            return
            
        p1, p2 = self.clipping_window
        min_x, max_x = min(p1.x, p2.x), max(p1.x, p2.x)
        min_y, max_y = min(p1.y, p2.y), max(p1.y, p2.y)
        
        # Define 4 clipping planes: left, right, bottom, top
        glEnable(GL_CLIP_PLANE0)  # Left
        glEnable(GL_CLIP_PLANE1)  # Right  
        glEnable(GL_CLIP_PLANE2)  # Bottom
        glEnable(GL_CLIP_PLANE3)  # Top
        
        # Clip planes equation: ax + by + cz + d = 0
        # Untuk 2D: z = 0, jadi ax + by + d = 0
        glClipPlane(GL_CLIP_PLANE0, [1, 0, 0, -min_x])   # x >= min_x
        glClipPlane(GL_CLIP_PLANE1, [-1, 0, 0, max_x])   # x <= max_x
        glClipPlane(GL_CLIP_PLANE2, [0, 1, 0, -min_y])   # y >= min_y
        glClipPlane(GL_CLIP_PLANE3, [0, -1, 0, max_y])   # y <= max_y

    def disable_opengl_clipping(self):
        """Matikan clipping planes"""
        glDisable(GL_CLIP_PLANE0)
        glDisable(GL_CLIP_PLANE1)
        glDisable(GL_CLIP_PLANE2)
        glDisable(GL_CLIP_PLANE3)

    def rectangle_intersects_window(self, p1, p2):
        """Cek apakah rectangle berpotongan dengan window"""
        if not self.clipping_window:
            return True
            
        win_p1, win_p2 = self.clipping_window
        win_min_x, win_max_x = min(win_p1.x, win_p2.x), max(win_p1.x, win_p2.x)
        win_min_y, win_max_y = min(win_p1.y, win_p2.y), max(win_p1.y, win_p2.y)
        
        rect_min_x, rect_max_x = min(p1.x, p2.x), max(p1.x, p2.x)
        rect_min_y, rect_max_y = min(p1.y, p2.y), max(p1.y, p2.y)
        
        # Rectangle overlap test - classic algorithm
        return not (rect_max_x < win_min_x or rect_min_x > win_max_x or 
                   rect_max_y < win_min_y or rect_min_y > win_max_y)

    def ellipse_intersects_window(self, center, width, height):
        """Cek apakah ellipse berpotongan dengan window (simplified bounding box)"""
        if not self.clipping_window:
            return True
            
        win_p1, win_p2 = self.clipping_window
        win_min_x, win_max_x = min(win_p1.x, win_p2.x), max(win_p1.x, win_p2.x)
        win_min_y, win_max_y = min(win_p1.y, win_p2.y), max(win_p1.y, win_p2.y)
        
        # Pakai bounding box ellipse (approximation, tapi cukup untuk most cases)
        ellipse_min_x = center.x - width/2
        ellipse_max_x = center.x + width/2
        ellipse_min_y = center.y - height/2
        ellipse_max_y = center.y + height/2
        
        return not (ellipse_max_x < win_min_x or ellipse_min_x > win_max_x or 
                   ellipse_max_y < win_min_y or ellipse_min_y > win_max_y)

    def update_continuous_transformations(self):                               # C.5) TRANSFORMASI VIA KEYBOARD
        """Update transformasi kontinyu berdasarkan tombol yang ditekan"""
        if self.selected_shape_index < 0 or self.selected_shape_index >= len(self.shapes):
            return
            
        selected_shape = self.shapes[self.selected_shape_index]
        
        # Rotasi kontinyu (smooth rotation saat hold key)
        if pygame.K_q in self.keys_pressed:  # Q = putar kiri
            self.apply_rotasi(selected_shape, -self.transform_speed['rotate'])
        if pygame.K_e in self.keys_pressed:  # E = putar kanan
            self.apply_rotasi(selected_shape, self.transform_speed['rotate'])
            
        # Translasi kontinyu (smooth movement seperti game)
        if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            self.apply_translasi(selected_shape, -self.transform_speed['translate'], 0)
        if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            self.apply_translasi(selected_shape, self.transform_speed['translate'], 0)
        if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
            self.apply_translasi(selected_shape, 0, -self.transform_speed['translate'])
        if pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
            self.apply_translasi(selected_shape, 0, self.transform_speed['translate'])
            
        # Scaling kontinyu
        if pygame.K_PAGEUP in self.keys_pressed or pygame.K_u in self.keys_pressed:
            self.apply_scaling(selected_shape, 1 + self.transform_speed['scale'])
        if pygame.K_PAGEDOWN in self.keys_pressed or pygame.K_j in self.keys_pressed:
            self.apply_scaling(selected_shape, 1 - self.transform_speed['scale'])

    def get_object_color(self, shape, shape_index):                            # D.7.a) OBJEK MASUK WINDOW = HIJAU
        """D.7.a) Tentukan warna objek berdasarkan posisi terhadap window"""    # D.7.b) OBJEK DILUAR WINDOW = CLIPPING
        # Priority 1: Selected shape = kuning (paling tinggi)
        if shape_index == self.selected_shape_index:
            return (1.0, 1.0, 0.0)  # Yellow
        
        # Priority 2: Objek dalam window = hijau (kalau ada window)
        if self.clipping_window:
            if shape.shape_type == 'titik':
                if self.point_inside_window(shape.transformed_points[0]):
                    return (0.0, 1.0, 0.0)  # Green - masuk ke window
                else:
                    return shape.color  # Warna asli jika di luar window
            elif shape.shape_type in ['garis', 'persegi', 'ellipse']:
                # Cek apakah ada point yang masuk window
                inside_count = sum(1 for p in shape.transformed_points if self.point_inside_window(p))
                if inside_count > 0:
                    return (0.0, 1.0, 0.0)  # Green - sebagian masuk ke window
                else:
                    return shape.color  # Warna asli jika sepenuhnya di luar window
        
        return shape.color  # Warna asli jika tidak ada window

    # ========== RENDERING SYSTEM ==========
    
    def render(self):
        """Main rendering function - ini yang dipanggil setiap frame"""
        glClear(GL_COLOR_BUFFER_BIT)  # Clear screen
        glClearColor(0.05, 0.05, 0.05, 1.0)  # Dark grey background
        glLoadIdentity()

        # BARU: Update window hover state berdasarkan mouse position
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos:
            mouse_x, mouse_y = self.screen_to_opengl(*mouse_pos)
            self.window_hover = self.is_mouse_on_window(mouse_x, mouse_y)

        # Enable clipping jika ada window
        if self.clipping_window:
            self.enable_opengl_clipping()

        # Render semua objek yang sudah jadi
        for i, shape in enumerate(self.shapes):
            points = shape.transformed_points  # Pakai transformed points (yang sudah di-transform)
            color = self.get_object_color(shape, i)  # Tentukan warna berdasarkan state
            
            if shape.shape_type == 'titik' and len(points) >= 1:
                # Gambar titik dengan ukuran yang sudah diatur
                self.draw_titik(points[0], color, self.current_point_size + shape.thickness)
                    
            elif shape.shape_type == 'garis' and len(points) >= 2:
                # Apply Cohen-Sutherland clipping untuk garis
                if self.clipping_window:
                    p1_clip, p2_clip, visible = self.cohen_sutherland_line_clipping(points[0], points[1])
                    if visible and p1_clip and p2_clip:
                        self.draw_garis(p1_clip, p2_clip, color, shape.thickness)
                    # Garis di luar window tidak digambar (ter-clip)
                else:
                    self.draw_garis(points[0], points[1], color, shape.thickness)
                    
            elif shape.shape_type == 'persegi' and len(points) >= 2:
                # Rectangle selalu digambar, tapi OpenGL clipping akan potong yang di luar
                if self.clipping_window:
                    self.draw_persegi(points[0], points[1], color, shape.thickness)
                else:
                    self.draw_persegi(points[0], points[1], color, shape.thickness)
                    
            elif shape.shape_type == 'ellipse' and len(points) >= 2:
                # Ellipse juga sama, OpenGL clipping yang handle
                center = Point((points[0].x + points[1].x) / 2, (points[0].y + points[1].y) / 2)
                width = abs(points[1].x - points[0].x)
                height = abs(points[1].y - points[0].y)
                if self.clipping_window:
                    self.draw_ellipse(center, width, height, color, shape.thickness)
                else:
                    self.draw_ellipse(center, width, height, color, shape.thickness)

        # Disable clipping setelah render objek utama
        if self.clipping_window:
            self.disable_opengl_clipping()

        # Gambar temporary points (titik merah saat lagi buat objek)
        for point in self.temp_points:
            self.draw_titik(point, (1.0, 0.0, 0.0), 8)

        # Preview real-time untuk objek multi-point (user experience improvement)
        if len(self.temp_points) == 1 and self.current_tool in ['garis', 'persegi', 'ellipse']:
            mouse_pos = pygame.mouse.get_pos()
            preview_point = Point(*self.screen_to_opengl(*mouse_pos))
            preview_color = (0.6, 0.6, 0.6)  # Abu-abu untuk preview
            
            if self.current_tool == 'garis':
                self.draw_garis(self.temp_points[0], preview_point, preview_color, 2)
            elif self.current_tool == 'persegi':
                self.draw_persegi(self.temp_points[0], preview_point, preview_color, 2)
            elif self.current_tool == 'ellipse':
                center = Point((self.temp_points[0].x + preview_point.x) / 2,
                              (self.temp_points[0].y + preview_point.y) / 2)
                width = abs(preview_point.x - self.temp_points[0].x)
                height = abs(preview_point.y - self.temp_points[0].y)
                if width > 5 and height > 5:  # Prevent tiny ellipses
                    self.draw_ellipse(center, width, height, preview_color, 2)

        # Gambar clipping window (selalu di atas, tidak ke-clip)
        self.draw_clipping_window()
        
        # Gambar preview window definition
        if self.defining_window and len(self.window_temp_points) == 1:
            mouse_pos = pygame.mouse.get_pos()
            preview_point = Point(*self.screen_to_opengl(*mouse_pos))
            
            # Gambar dashed line untuk preview window
            glColor3f(1.0, 0.5, 0.5)  # Pink muda
            glLineWidth(2)
            glEnable(GL_LINE_STIPPLE)
            glLineStipple(1, 0x5555)  # Dashed pattern
            glBegin(GL_LINE_LOOP)
            glVertex2f(self.window_temp_points[0].x, self.window_temp_points[0].y)
            glVertex2f(preview_point.x, self.window_temp_points[0].y)
            glVertex2f(preview_point.x, preview_point.y)
            glVertex2f(self.window_temp_points[0].x, preview_point.y)
            glEnd()
            glDisable(GL_LINE_STIPPLE)

        # Gambar UI info
        self.draw_ui_info()
        
        # Update transformasi kontinyu setiap frame
        self.update_continuous_transformations()
        
        pygame.display.flip()  # Swap buffer (double buffering)

    def draw_ui_info(self):
        """Gambar info UI di screen - visual feedback untuk user"""
        # Gambar kotak warna current color
        glColor3f(*self.current_color)
        glBegin(GL_QUADS)
        glVertex2f(10, 10)
        glVertex2f(40, 10)
        glVertex2f(40, 25)
        glVertex2f(10, 25)
        glEnd()
        
        # Indikator kalau ada objek yang selected
        if self.selected_shape_index >= 0:
            # Kotak kuning menandakan ada yang selected
            glColor3f(1.0, 1.0, 0.0)  # Yellow
            glBegin(GL_QUADS)
            glVertex2f(50, 10)
            glVertex2f(200, 10)
            glVertex2f(200, 25)
            glVertex2f(50, 25)
            glEnd()
            
            # Indikator rotation controls (visual hint)
            glColor3f(0.0, 1.0, 1.0)  # Cyan
            glLineWidth(2)
            # Q dan E rotation indicators
            for i, (x, direction) in enumerate([(10, -1), (30, 1)]):
                center_x, center_y = 60 + i * 40, 50
                radius = 12
                start_angle = 0 if direction > 0 else math.pi
                end_angle = math.pi if direction > 0 else 2 * math.pi
                
                # Gambar arc untuk show rotation direction
                glBegin(GL_LINE_STRIP)
                for j in range(10):
                    angle = start_angle + (end_angle - start_angle) * j / 9
                    px = center_x + radius * math.cos(angle)
                    py = center_y + radius * math.sin(angle)
                    glVertex2f(px, py)
                glEnd()
                
                # Arrow indicator
                arrow_angle = end_angle - 0.3 * direction
                ax1 = center_x + radius * math.cos(arrow_angle)
                ay1 = center_y + radius * math.sin(arrow_angle)
                ax2 = ax1 + 5 * math.cos(arrow_angle + 2.5 * direction)
                ay2 = ay1 + 5 * math.sin(arrow_angle + 2.5 * direction)
                ax3 = ax1 + 5 * math.cos(arrow_angle - 2.5 * direction)
                ay3 = ay1 + 5 * math.sin(arrow_angle - 2.5 * direction)
                
                glBegin(GL_TRIANGLES)
                glVertex2f(ax1, ay1)
                glVertex2f(ax2, ay2)
                glVertex2f(ax3, ay3)
                glEnd()
                
        # BARU: Indikator status window drag
        if self.clipping_window:
            if self.dragging_window:
                glColor3f(1.0, 0.5, 0.0)  # Orange untuk drag
                text_y = 35
            elif self.window_hover:
                glColor3f(1.0, 1.0, 0.0)  # Kuning untuk hover
                text_y = 35
            else:
                glColor3f(0.0, 1.0, 0.0)  # Hijau untuk window aktif
                text_y = 35
                
            # Gambar indikator kotak kecil untuk status window
            glBegin(GL_QUADS)
            glVertex2f(210, text_y)
            glVertex2f(240, text_y)
            glVertex2f(240, text_y + 15)
            glVertex2f(210, text_y + 15)
            glEnd()

    # ========== EVENT HANDLING ==========
    
    def handle_mouse_click(self, pos):                                         # A.2) KOORDINAT INPUT VIA MOUSE KLIK
        """A.2) Handle klik mouse - ini yang convert mouse input jadi objek"""
        x, y = self.screen_to_opengl(*pos)
        point = Point(x, y)
        
        # BARU: Prioritas pertama - cek apakah klik di window untuk drag
        if not self.defining_window and self.start_window_drag(x, y):
            return  # Klik di window untuk drag, tidak buat objek
        
        if self.defining_window:                                               # D.6) WINDOW AKTIF: KLIK 2 TITIK SUDUT
            # Mode buat window - butuh 2 klik
            self.window_temp_points.append(point)
            if len(self.window_temp_points) == 2:
                self.define_clipping_window(self.window_temp_points[0], self.window_temp_points[1])
                self.window_temp_points = []
                self.defining_window = False
        else:
            # Mode buat objek normal
            self.temp_points.append(point)
            
            if self.current_tool == 'titik':
                # Titik cuma butuh 1 klik langsung jadi
                shape = Shape('titik', [point], self.current_color, self.current_thickness)
                self.shapes.append(shape)
                self.temp_points = []
                print(f"✓ Titik dibuat di ({x:.0f}, {y:.0f})")
                
            elif self.current_tool in ['garis', 'persegi', 'ellipse'] and len(self.temp_points) == 2:
                # Objek lain butuh 2 klik baru jadi
                shape = Shape(self.current_tool, self.temp_points.copy(), self.current_color, self.current_thickness)
                self.shapes.append(shape)
                self.temp_points = []
                print(f"✓ {self.current_tool.capitalize()} berhasil dibuat")

    def handle_mouse_release(self, pos):
        """BARU: Handle mouse button release - untuk stop drag window"""
        self.stop_window_drag()

    def handle_mouse_motion(self, pos):
        """BARU: Handle mouse motion - untuk update drag window"""
        if self.dragging_window:
            x, y = self.screen_to_opengl(*pos)
            self.update_window_drag(x, y)

    def handle_keyboard(self, key):                                            # C.5) TRANSFORMASI VIA KEYBOARD
        """Handle input keyboard - ini inti dari kontrol program"""
        
        # A.1) Tool selection - angka 1-4 untuk pilih tool
        if key == pygame.K_1:                                                  # A.1.a) TOOL TITIK
            self.current_tool = 'titik'
            self.temp_points = []
            print("🔧 Tool: TITIK (klik 1x)")
        elif key == pygame.K_2:                                                # A.1.b) TOOL GARIS
            self.current_tool = 'garis'
            self.temp_points = []
            print("🔧 Tool: GARIS (klik 2x)")
        elif key == pygame.K_3:                                                # A.1.c) TOOL PERSEGI
            self.current_tool = 'persegi'
            self.temp_points = []
            print("🔧 Tool: PERSEGI (klik 2x)")
        elif key == pygame.K_4:                                                # A.1.d) TOOL ELLIPSE
            self.current_tool = 'ellipse'
            self.temp_points = []
            print("🔧 Tool: ELLIPSE (klik 2x)")

        # B.3.a) Color selection - huruf untuk warna                          # B.3.a) WARNA OBJEK VIA SHORTCUT
        elif key == pygame.K_r:
            self.set_color_by_name('merah')
        elif key == pygame.K_g:
            self.set_color_by_name('hijau')
        elif key == pygame.K_b:
            self.set_color_by_name('biru')
        elif key == pygame.K_w:
            self.set_color_by_name('putih')
        elif key == pygame.K_y:
            self.set_color_by_name('kuning')
        elif key == pygame.K_c and pygame.key.get_pressed()[pygame.K_LSHIFT]:  # Shift+C untuk cyan
            self.set_color_by_name('cyan')
        elif key == pygame.K_m:
            self.set_color_by_name('magenta')

        # B.3.b) Thickness adjustment                                         # B.3.b) KETEBALAN GARIS
        elif key == pygame.K_PLUS :
            self.adjust_thickness(1)
        elif key == pygame.K_MINUS:
            self.adjust_thickness(-1)

        # BARU: Point size adjustment
        elif key == pygame.K_PERIOD:  # . = besarkan titik
            self.adjust_point_size(2)
        elif key == pygame.K_COMMA:  # , = kecilkan titik
            self.adjust_point_size(-2)

        # C.5) Selection dan transformasi
        elif key == pygame.K_s and not (pygame.K_LSHIFT in self.keys_pressed):
            # S = select next shape untuk transformasi
            if self.shapes:
                self.selected_shape_index = (self.selected_shape_index + 1) % len(self.shapes)
                print(f"👆 Shape {self.selected_shape_index} dipilih (kuning)")
                print("🎮 KONTROL KONTINYU AKTIF:")
                print("   Q/E = Putar kiri/kanan    WASD/Arrow = Gerak")
                print("   U/J = Scale up/down       Hold tombol untuk kontrol smooth!")
            else:
                print("❌ Tidak ada objek untuk dipilih")
                
        # INSTANT transformations (sekali tekan langsung transform)
        elif key == pygame.K_t:                                                # C.4.a) TRANSFORMASI TRANSLASI INSTANT
            # T = translasi instant
            if self.selected_shape_index >= 0:
                self.apply_translasi(self.shapes[self.selected_shape_index], 25, 0)
                print("↔️ Translasi instant (+25px ke kanan)")
            else:
                print("❌ Pilih objek dulu dengan 'S'")
                
        elif key == pygame.K_z:                                                # C.4.b) TRANSFORMASI ROTASI INSTANT
            # Z = rotasi instant
            if self.selected_shape_index >= 0:
                self.apply_rotasi(self.shapes[self.selected_shape_index], 15)
                print("🔄 Rotasi instant 15°")
            else:
                print("❌ Pilih objek dulu dengan 'S'")
                
        elif key == pygame.K_x:                                                # C.4.c) TRANSFORMASI SCALING INSTANT
            # X = scale up instant
            if self.selected_shape_index >= 0:
                self.apply_scaling(self.shapes[self.selected_shape_index], 1.2)
                print("🔍 Scale up instant 1.2x")
            else:
                print("❌ Pilih objek dulu dengan 'S'")
                
        elif key == pygame.K_v:                                                # C.4.c) TRANSFORMASI SCALING INSTANT
            # V = scale down instant
            if self.selected_shape_index >= 0:
                self.apply_scaling(self.shapes[self.selected_shape_index], 0.8)
                print("🔍 Scale down instant 0.8x")
            else:
                print("❌ Pilih objek dulu dengan 'S'")

        # D.6) Window definition dan management                                # D.8) WINDOW DIGESER/DIUBAH UKURAN
        elif key == pygame.K_o:                                                # D.6) WINDOW AKTIF: O + KLIK 2 SUDUT
            # O = buat window baru
            self.defining_window = True
            self.window_temp_points = []
            print("🪟 Mode Window: Klik 2 titik sudut untuk definisi window clipping")

        elif key == pygame.K_p:  # P = hapus window                           # D.8) HAPUS WINDOW
            if self.clipping_window:
                self.clipping_window = None
                print("🗑️ Window clipping dihapus")
            else:
                print("❌ Tidak ada window untuk dihapus")
                
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:              # D.8) HAPUS WINDOW (ALTERNATIF)
            # Delete/Backspace = hapus window (alternatif)
            if self.clipping_window:
                self.clipping_window = None
                print("🗑️ Window clipping dihapus (Delete)")
            else:
                print("❌ Tidak ada window untuk dihapus")

        # Utility commands
        elif key == pygame.K_c and not pygame.key.get_pressed()[pygame.K_LSHIFT]:
            # C = clear all (tapi bukan Shift+C yang untuk cyan)
            self.shapes = []
            self.temp_points = []
            self.selected_shape_index = -1
            print("🗑️ Semua objek dihapus")
            
        elif key == pygame.K_SPACE:
            # Space = tampilkan help
            self.print_detailed_instructions()
            
        # PENTING: Tambahin key ke set untuk continuous controls
        self.keys_pressed.add(key)

    def print_detailed_instructions(self):
        """Print instruksi lengkap - documentation dalam program"""
        print("\n" + "="*80)
        print("📖 MODUL A: OBJEK 2D - INSTRUKSI LENGKAP (DENGAN DRAGGABLE WINDOW)")
        print("="*80)
        
        print("\n🎯 A. FUNGSI PENGGAMBARAN OBJEK")
        print("   1. Gambar Objek Dasar:")
        print("      a) Titik    → Tekan '1', lalu klik 1x di canvas")        # A.1.a) GAMBAR TITIK
        print("      b) Garis    → Tekan '2', lalu klik 2x di canvas")        # A.1.b) GAMBAR GARIS
        print("      c) Persegi  → Tekan '3', lalu klik 2x di canvas")        # A.1.c) GAMBAR PERSEGI
        print("      d) Ellipse  → Tekan '4', lalu klik 2x di canvas")        # A.1.d) GAMBAR ELLIPSE
        print("   2. Koordinat input dilakukan dengan klik mouse pada canvas OpenGL")  # A.2) INPUT KOORDINAT MOUSE
        
        print("\n🎨 B. FUNGSI WARNA & KETEBALAN")
        print("   3. Pengguna dapat memilih:")
        print("      a) Warna objek (melalui tombol atau shortcut keyboard):") # B.3.a) WARNA VIA SHORTCUT
        print("         R = Merah    G = Hijau    B = Biru    W = Putih")
        print("         Y = Kuning   M = Magenta  Shift+C = Cyan")
        print("      b) Ketebalan garis (jika menggunakan GL_LINES atau GL_LINE_LOOP):") # B.3.b) KETEBALAN GARIS
        print("         + = Tambah ketebalan    - = Kurangi ketebalan")
        print("      c) Ukuran titik:")
        print("         . (titik) = Besarkan titik    , (koma) = Kecilkan titik")
        
        print("\n🔄 C. TRANSFORMASI GEOMETRI")
        print("   4. Objek yang telah digambar dapat dikenai transformasi:")
        print("      a) Translasi → S (pilih objek) + T (instant) atau WASD/Arrow (kontinyu)")  # C.4.a) TRANSLASI
        print("      b) Rotasi    → S (pilih objek) + Z (instant) atau Q/E (kontinyu)")         # C.4.b) ROTASI
        print("      c) Scaling   → S (pilih objek) + X/V (instant) atau U/J (kontinyu)")       # C.4.c) SCALING
        print("   5. Transformasi dilakukan melalui keyboard:")                                  # C.5) TRANSFORMASI VIA KEYBOARD
        print("      🎮 INSTANT (sekali tekan): T, Z, X, V")
        print("      🎮 KONTINYU (tahan tombol): Q/E (putar), WASD/Arrow (gerak), U/J (scale)")
        
        print("\n🪟 D. WINDOWING DAN CLIPPING (DENGAN DRAG SUPPORT)")
        print("   6. Pengguna dapat menentukan window aktif:")                                   # D.6) WINDOW AKTIF
        print("      → Tekan 'O', lalu klik 2 titik sudut sebagai batas window")
        print("   7. Objek yang:")
        print("      a) Masuk ke window: akan berubah warna (menjadi HIJAU)")                   # D.7.a) OBJEK MASUK = HIJAU
        print("      b) Di luar window: HIDE / TIDAK TERLIHAT tapi terpotong")                  # D.7.b) OBJEK LUAR = CLIPPING
        print("         (gunakan algoritma Cohen-Sutherland untuk garis)")
        print("   8. Window dapat digeser atau diubah ukurannya:")                              # D.8) WINDOW DIGESER/DIUBAH
        print("      🖱️ DRAG WINDOW: Klik dan drag window untuk geser posisi")
        print("         - Hover di window → window jadi KUNING + cross icon")
        print("         - Drag window → window jadi ORANGE")
        print("         - Window normal → MERAH dengan corner markers")
        print("      🗑️ P = Hapus window")
        print("      🗑️ Delete/Backspace = Hapus window")
        print("      🆕 O = Buat window baru")
        
        print("\n🛠️ KONTROL TAMBAHAN:")
        print("   C = Clear semua objek")
        print("   SPACE = Tampilkan instruksi ini")
        print("   ESC = Keluar program")
        print("   . (titik) = Besarkan ukuran titik")
        print("   , (koma) = Kecilkan ukuran titik")
        
        print("\n💡 WORKFLOW RECOMMENDED:")
        print("   1. Pilih tool (1-4) → Pilih warna (R/G/B/W/Y/M) → Klik di canvas")
        print("   2. Untuk transformasi:")
        print("      📱 S (pilih objek kuning) → T/Z/X/V (instant)")
        print("      🎮 S (pilih objek kuning) → TAHAN Q/E/WASD/U/J (smooth control)")
        print("   3. Untuk clipping:")
        print("      🆕 O → klik 2 sudut (buat window)")
        print("      🖱️ DRAG window untuk geser posisi (visual feedback)")
        print("      🗑️ P atau Delete (hapus window)")
        print("      🟢 Objek dalam window = HIJAU")  
        print("      🔴 Objek luar window = TERPOTONG")
        print("   4. Untuk ukuran titik:")
        print("      . (titik) = Besarkan    , (koma) = Kecilkan")
        print("\n🆕 FITUR BARU - DRAGGABLE WINDOW:")
        print("   🖱️ Hover mouse di window → Kuning + Cross icon")
        print("   🖱️ Klik dan drag window → Orange saat drag")
        print("   🖱️ Release mouse → Window tetap di posisi baru")
        print("   🔒 Window tidak bisa keluar dari screen boundaries")
        print("="*80)

    def run(self):
        """Main program loop - ini yang jalan terus selama program aktif"""
        self.print_detailed_instructions()
        clock = pygame.time.Clock()  # Untuk maintain 60 FPS
        
        print("\n🚀 Program dimulai! Tekan SPACE untuk melihat instruksi lagi.")
        print("   Mulai dengan: 1 (titik) + R (merah) + klik di canvas")
        print("   Ukuran titik: . (besarkan) , (kecilkan)")
        print("🆕 DRAG WINDOW: O (buat window) → Drag untuk geser!")
        
        while self.running:
            # Event loop - handle semua input dari user
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # User close window
                    self.running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click only
                        self.handle_mouse_click(event.pos)
                        
                elif event.type == pygame.MOUSEBUTTONUP:  # BARU: Mouse button release
                    if event.button == 1:  # Left click release
                        self.handle_mouse_release(event.pos)
                        
                elif event.type == pygame.MOUSEMOTION:  # BARU: Mouse motion
                    self.handle_mouse_motion(event.pos)
                        
                elif event.type == pygame.KEYDOWN:  # Key ditekan
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.handle_keyboard(event.key)
                        
                elif event.type == pygame.KEYUP:  # Key dilepas
                    # PENTING: Hapus dari set untuk stop continuous transform
                    self.keys_pressed.discard(event.key)
            
            # Render frame dan maintain 60 FPS
            self.render()
            clock.tick(60)
        
        # Cleanup saat exit
        pygame.quit()
        sys.exit()

# Entry point program
if __name__ == "__main__":
    program = OpenGL2DModulA()  # Buat instance program
    program.run()  # Jalankan main loop
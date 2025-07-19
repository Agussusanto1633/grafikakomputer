import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
import sys

class ProfessionalObject3D:
    def __init__(self):
        # Parameter transformasi dengan smooth interpolation (animasi halus)
        self.rotation_x = 0.0                                                  # 2) TRANSFORMASI ROTASI (X-AXIS)
        self.rotation_y = 0.0                                                  # 2) TRANSFORMASI ROTASI (Y-AXIS)
        self.rotation_z = 0.0                                                  # 2) TRANSFORMASI ROTASI (Z-AXIS)
        self.target_rotation_x = 0.0  # Target untuk smooth rotation
        self.target_rotation_y = 0.0  # Rotasi akan bergerak ke target ini secara halus
        
        self.translation_x = 0.0                                               # 2) TRANSFORMASI TRANSLASI (X-AXIS)
        self.translation_y = 0.0                                               # 2) TRANSFORMASI TRANSLASI (Y-AXIS)
        self.translation_z = -6.0  # Mundur 6 unit biar objek keliatan        # 2) TRANSFORMASI TRANSLASI (Z-AXIS)
        self.scale = 1.0
        
        # Animasi dan interaksi
        self.auto_rotate = False  # Auto rotation on/off
        self.rotation_speed = 1.0  # Kecepatan auto rotation
        self.animation_time = 0.0  # Timer untuk animasi
        
        # Properties objek
        self.current_object = "cube"  # Objek yang aktif: "cube" atau "pyramid"  # 1.a) KUBUS ATAU PIRAMIDA
        self.wireframe_mode = False   # Mode wireframe (garis aja) atau solid
        
        # Advanced lighting system (pencahayaan profesional)
        self.lighting_enabled = True
        self.shading_mode = "phong"  # "phong" (smooth) atau "gouraud" (flat)  # 3.a) MODEL PENCAHAYAAN PHONG/GOURAUD
        self.light_position = [2.0, 2.0, 2.0, 1.0]  # Posisi lampu [x, y, z, w]
        self.light_ambient = [0.3, 0.3, 0.3, 1.0]   # Cahaya ambient (background)  # 3.b) AMBIENT LIGHT
        self.light_diffuse = [0.8, 0.8, 0.8, 1.0]   # Cahaya diffuse (utama)      # 3.b) DIFFUSE LIGHT
        self.light_specular = [1.0, 1.0, 1.0, 1.0]  # Cahaya specular (kilauan)   # 3.b) SPECULAR LIGHT
        
        # Material properties (sifat permukaan objek)
        self.material_shininess = 128.0  # Tingkat kilauan (0-128)
        self.material_specular = [1.0, 1.0, 1.0, 1.0]  # Warna specular
        
        # UI dan interaksi
        self.show_info = True  # Tampilkan info panel atau tidak
        self.mouse_sensitivity = 0.5  # Sensitivitas mouse untuk rotate           # 2) TRANSFORMASI VIA MOUSE DRAG
        self.movement_speed = 0.05     # Kecepatan movement WASD                  # 2) TRANSFORMASI VIA KEYBOARD
        
    def setup_advanced_lighting(self):                                         # 3) SHADING & PENCAHAYAAN SETUP
        """Setup pencahayaan profesional dengan kontrol penuh - INI YANG BIKIN 3D KELIATAN REALISTIS!"""
        # Enable fitur-fitur lighting OpenGL
        glEnable(GL_LIGHTING)      # Aktifkan sistem lighting                   # 3) ENABLE LIGHTING SYSTEM
        glEnable(GL_LIGHT0)        # Lampu utama                                # 3.b) LIGHT SOURCE 0
        glEnable(GL_LIGHT1)        # Lampu kedua untuk efek yang lebih dramatis # 3.b) LIGHT SOURCE 1
        glEnable(GL_DEPTH_TEST)    # Depth testing biar objek di depan nutupin yang di belakang
        glEnable(GL_COLOR_MATERIAL) # Material bisa ikut warna vertex
        glEnable(GL_NORMALIZE)     # Normalize normal vectors otomatis (penting!)
        glEnable(GL_BLEND)         # Alpha blending untuk transparansi
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Main light (LIGHT0) - lampu utama
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.light_ambient)   # Cahaya background  # 3.b) AMBIENT LIGHT IMPLEMENTATION
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.light_diffuse)   # Cahaya utama       # 3.b) DIFFUSE LIGHT IMPLEMENTATION
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.light_specular) # Cahaya kilauan     # 3.b) SPECULAR LIGHT IMPLEMENTATION
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position) # Posisi lampu
        
        # Secondary light (LIGHT1) - fill light biar tidak terlalu kontras
        fill_light_pos = [-1.0, -1.0, 1.0, 1.0]
        fill_light_diffuse = [0.3, 0.3, 0.4, 1.0]  # Biru muda untuk fill
        glLightfv(GL_LIGHT1, GL_DIFFUSE, fill_light_diffuse)
        glLightfv(GL_LIGHT1, GL_POSITION, fill_light_pos)
        
        # Global ambient - cahaya yang ada di mana-mana (prevent total darkness)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)  # Lighting untuk kedua sisi polygon
        
        # Material properties - sifat permukaan objek
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.material_specular)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.material_shininess)
        
    def set_advanced_shading_mode(self, mode):                                 # 3.a) IMPLEMENTASI MODEL PENCAHAYAAN
        """Set model pencahayaan dengan kualitas tinggi"""
        self.shading_mode = mode
        if mode == "phong":                                                    # 3.a) PHONG SHADING MODEL
            # Phong shading = smooth, interpolasi warna antar vertex
            glShadeModel(GL_SMOOTH)
            glEnable(GL_POLYGON_SMOOTH)    # Anti-aliasing untuk polygon
            glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)  # Kualitas terbaik
        elif mode == "gouraud":                                                # 3.a) GOURAUD SHADING MODEL
            # Gouraud shading = flat, warna per face
            glShadeModel(GL_FLAT)
            glDisable(GL_POLYGON_SMOOTH)
    
    def draw_smooth_cube(self):                                                # 1.a) KUBUS 3D OBJECT
        """Menggambar kubus dengan kualitas tinggi dan normal vectors yang akurat"""
        # Vertices dengan koordinat yang lebih presisi (pakai numpy untuk performa)
        size = 1.0
        vertices = np.array([                                                  # 1.b) VERTEX DEFINITION MANUAL
            # 8 titik vertex kubus (x, y, z)
            [-size, -size, -size], [size, -size, -size], [size, size, -size], [-size, size, -size],  # back face
            [-size, -size, size], [size, -size, size], [size, size, size], [-size, size, size]       # front face
        ], dtype=np.float32)
        
        # Faces dengan normal vectors yang tepat - INI KUNCI LIGHTING YANG BAGUS!
        # Format: (vertex_indices, normal_vector, color_rgba)
        faces_data = [                                                         # 1.b) FACE DEFINITION MANUAL
            ([0, 1, 2, 3], [0, 0, -1], [0.8, 0.2, 0.2, 0.9]),  # back face - red
            ([4, 7, 6, 5], [0, 0, 1], [0.2, 0.8, 0.2, 0.9]),   # front face - green  
            ([0, 4, 5, 1], [0, -1, 0], [0.2, 0.2, 0.8, 0.9]),  # bottom face - blue
            ([2, 6, 7, 3], [0, 1, 0], [0.8, 0.8, 0.2, 0.9]),   # top face - yellow
            ([0, 3, 7, 4], [-1, 0, 0], [0.8, 0.2, 0.8, 0.9]),  # left face - magenta
            ([1, 5, 6, 2], [1, 0, 0], [0.2, 0.8, 0.8, 0.9])    # right face - cyan
        ]
        
        # Set polygon mode (wireframe atau solid)
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  # Wireframe mode
            glLineWidth(2.0)  # Tebal garis
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Solid mode
        
        # Render setiap face dengan GL_QUADS (4 vertex per face)
        glBegin(GL_QUADS)
        for face_indices, normal, color in faces_data:
            glNormal3fv(normal)  # Set normal vector (PENTING untuk lighting!)
            glColor4fv(color)    # Set warna face
            for vertex_idx in face_indices:
                glVertex3fv(vertices[vertex_idx])  # Render vertex
        glEnd()
    
    def draw_smooth_pyramid(self):                                             # 1.a) PIRAMIDA 3D OBJECT
        """Menggambar piramida dengan kualitas tinggi"""
        height = 1.5
        base_size = 1.0
        
        # 5 vertices: 1 apex (puncak) + 4 base corners
        vertices = np.array([                                                  # 1.b) VERTEX DEFINITION MANUAL
            [0, height, 0],                      # apex (puncak)
            [-base_size, -height/2, base_size],   # base front left
            [base_size, -height/2, base_size],    # base front right
            [base_size, -height/2, -base_size],   # base back right
            [-base_size, -height/2, -base_size]   # base back left
        ], dtype=np.float32)
        
        # Triangle faces untuk sisi piramida (3 vertex per face)
        triangle_faces = [                                                     # 1.b) FACE DEFINITION MANUAL
            ([0, 1, 2], [0.8, 0.2, 0.2, 0.9]),  # front triangle - red
            ([0, 2, 3], [0.2, 0.8, 0.2, 0.9]),  # right triangle - green
            ([0, 3, 4], [0.2, 0.2, 0.8, 0.9]),  # back triangle - blue
            ([0, 4, 1], [0.8, 0.8, 0.2, 0.9])   # left triangle - yellow
        ]
        
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(2.0)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # Draw triangular faces
        glBegin(GL_TRIANGLES)
        for face_indices, color in triangle_faces:
            # Calculate normal vector secara matematis (cross product)
            v1 = vertices[face_indices[1]] - vertices[face_indices[0]]  # Vector edge 1
            v2 = vertices[face_indices[2]] - vertices[face_indices[0]]  # Vector edge 2
            normal = np.cross(v1, v2)  # Cross product = normal vector
            normal = normal / np.linalg.norm(normal)  # Normalize (panjang = 1)
            
            glNormal3fv(normal)
            glColor4fv(color)
            for vertex_idx in face_indices:
                glVertex3fv(vertices[vertex_idx])
        glEnd()
        
        # Draw base (alas piramida) - quad
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)  # Normal pointing down
        glColor4f(0.8, 0.2, 0.8, 0.9)  # magenta base
        base_indices = [1, 4, 3, 2]  # Base vertices dalam urutan yang benar
        for vertex_idx in base_indices:
            glVertex3fv(vertices[vertex_idx])
        glEnd()
    
    def draw_object(self):                                                     # 1) VISUALISASI OBJEK 3D
        """Menggambar objek dengan kualitas profesional"""
        # Apply smooth transformations (rotasi yang halus)
        self.smooth_interpolate_rotations()
        
        # Switch objek berdasarkan current_object
        if self.current_object == "cube":                                      # 1.a) RENDER KUBUS
            self.draw_smooth_cube()
        elif self.current_object == "pyramid":                                 # 1.a) RENDER PIRAMIDA
            self.draw_smooth_pyramid()
    
    def smooth_interpolate_rotations(self):
        """Smooth interpolation untuk rotasi yang halus - LERP (Linear Interpolation)"""
        lerp_factor = 0.1  # Factor interpolasi (0.1 = 10% per frame menuju target)
        # Formula LERP: current = current + (target - current) * factor
        self.rotation_x += (self.target_rotation_x - self.rotation_x) * lerp_factor
        self.rotation_y += (self.target_rotation_y - self.rotation_y) * lerp_factor
    
    def apply_professional_transformations(self):                              # 2) TRANSFORMASI OBJEK 3D
        """Transformasi dengan animasi smooth - URUTAN PENTING!"""
        glLoadIdentity()  # Reset matrix transformasi
        
        # Auto rotation jika diaktifkan
        if self.auto_rotate:
            self.animation_time += 0.016  # ~60 FPS (1/60 = 0.016 second per frame)
            self.rotation_y += self.rotation_speed
        
        # Apply transformations dengan urutan yang benar: TRS (Translate, Rotate, Scale)
        glTranslatef(self.translation_x, self.translation_y, self.translation_z)  # 2) TRANSLASI IMPLEMENTATION
        glRotatef(self.rotation_x, 1, 0, 0)  # 2. Rotate X                        # 2) ROTASI IMPLEMENTATION (X)
        glRotatef(self.rotation_y, 0, 1, 0)  # 2. Rotate Y                        # 2) ROTASI IMPLEMENTATION (Y)
        glRotatef(self.rotation_z, 0, 0, 1)  # 2. Rotate Z                        # 2) ROTASI IMPLEMENTATION (Z)
        glScalef(self.scale, self.scale, self.scale)  # 3. Scale uniform
    
    def setup_professional_perspective(self, width, height):                   # 4) KAMERA DAN PERSPEKTIF
        """Setup kamera dengan kualitas profesional"""
        glMatrixMode(GL_PROJECTION)  # Switch ke projection matrix
        glLoadIdentity()
        
        # Setup perspective dengan FOV yang optimal
        aspect_ratio = width / height
        gluPerspective(60.0, aspect_ratio, 0.1, 100.0)  # 60° FOV untuk perspektif natural  # 4.b) gluPerspective UNTUK 3D
        # Parameter: FOV_degrees, aspect_ratio, near_plane, far_plane
        
        glMatrixMode(GL_MODELVIEW)  # Switch balik ke modelview matrix
        glLoadIdentity()
        
        # Professional camera setup dengan gluLookAt
        gluLookAt(0, 0, 0,      # eye position (posisi kamera)                 # 4.a) gluLookAt POSISI KAMERA
                  0, 0, -1,     # look at point (ke mana kamera nengok)
                  0, 1, 0)      # up vector (arah atas kamera)
        
        # Setup viewport dengan precision
        glViewport(0, 0, width, height)  # Area render dalam window
    
    def animate_light(self):
        """Animasi cahaya untuk efek dramatic - cahaya bergerak melingkar"""
        time = self.animation_time
        # Gerakan circular dengan trigonometry
        self.light_position[0] = 3.0 * math.cos(time * 0.5)  # X position
        self.light_position[2] = 3.0 * math.sin(time * 0.5)  # Z position
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)  # Update posisi lampu
    
    def render_ui_info(self, surface, font):
        """Render informasi UI yang profesional - overlay info panel"""
        if not self.show_info:
            return
            
        # List informasi yang ditampilkan
        info_lines = [
            f"Object: {self.current_object.upper()}",
            f"Shading: {self.shading_mode.upper()}",
            f"Lighting: {'ON' if self.lighting_enabled else 'OFF'}",
            f"Wireframe: {'ON' if self.wireframe_mode else 'OFF'}",
            f"Auto Rotate: {'ON' if self.auto_rotate else 'OFF'}",
            "",
            "=== CONTROLS ===",
            "Mouse Drag: Rotate",                                              # 2) ROTASI VIA MOUSE DRAG
            "WASD + QE: Move",                                                 # 2) TRANSLASI VIA KEYBOARD
            "C: Change Object",
            "L: Toggle Lighting", 
            "1/2: Phong/Gouraud",                                              # 3.a) TOGGLE SHADING MODEL
            "F: Wireframe Mode",
            "R: Auto Rotate",
            "H: Hide/Show Info",
            "ESC: Exit"
        ]
        
        y_offset = 10
        for line in info_lines:
            if line.startswith("==="):
                color = (255, 255, 0)  # Yellow untuk headers
            elif line == "":
                y_offset += 10  # Spasi kosong
                continue
            else:
                color = (255, 255, 255)  # White untuk text normal
                
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (10, y_offset))
            y_offset += 20

def main():
    pygame.init()
    
    # Professional window setup
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | pygame.RESIZABLE)
    pygame.display.set_caption("Professional 3D Object Visualization | Modul B")
    
    # Font untuk UI overlay
    font = pygame.font.Font(None, 24)
    ui_surface = pygame.Surface((width, height))  # Surface untuk UI overlay
    ui_surface.set_colorkey((0, 0, 0))  # Black = transparent
    
    # Initialize 3D object
    obj3d = ProfessionalObject3D()
    obj3d.setup_professional_perspective(width, height)                        # 4) SETUP KAMERA & PERSPEKTIF
    obj3d.setup_advanced_lighting()                                           # 3) SETUP LIGHTING SYSTEM
    obj3d.set_advanced_shading_mode("phong")                                  # 3.a) SET PHONG SHADING
    
    # Professional OpenGL settings
    glClearColor(0.1, 0.1, 0.15, 1.0)  # Dark blue background (profesional look)
    glEnable(GL_MULTISAMPLE)  # Anti-aliasing untuk edge yang halus
    
    # Interaction variables
    clock = pygame.time.Clock()
    mouse_dragging = False  # Status mouse drag
    last_mouse_pos = (0, 0)  # Posisi mouse terakhir
    
    # Print startup info
    print("🎮 PROFESSIONAL 3D VISUALIZATION")
    print("=" * 40)
    print("✨ Enhanced Features:")
    print("   • Smooth interpolated rotations")  # LERP animation
    print("   • Advanced lighting system")       # Multi-light setup
    print("   • Professional shading")           # Phong/Gouraud
    print("   • Wireframe mode")                 # Toggle solid/wireframe
    print("   • Auto rotation")                  # Auto animate
    print("   • Animated lighting")              # Moving light source
    print("   • High-quality rendering")         # Anti-aliasing, etc.
    print("=" * 40)
    
    running = True
    while running:
        # Handle events (input dari user)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize (responsive design)
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | pygame.RESIZABLE)
                obj3d.setup_professional_perspective(width, height)
                ui_surface = pygame.Surface((width, height))
                ui_surface.set_colorkey((0, 0, 0))
            elif event.type == pygame.KEYDOWN:
                # Handle key press events
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:                                  # 1.a) CHANGE OBJECT (CUBE/PYRAMID)
                    # C = Change object (toggle cube/pyramid)
                    obj3d.current_object = "pyramid" if obj3d.current_object == "cube" else "cube"
                    print(f"🔄 Object changed to: {obj3d.current_object.upper()}")
                elif event.key == pygame.K_l:                                  # 3) TOGGLE LIGHTING ON/OFF
                    # L = Toggle lighting on/off
                    obj3d.lighting_enabled = not obj3d.lighting_enabled
                    if obj3d.lighting_enabled:
                        glEnable(GL_LIGHTING)
                        print("💡 Lighting: ON")
                    else:
                        glDisable(GL_LIGHTING)
                        print("🔆 Lighting: OFF")
                elif event.key == pygame.K_1:                                  # 3.a) PHONG SHADING MODEL
                    # 1 = Phong shading (smooth)
                    obj3d.set_advanced_shading_mode("phong")
                    print("✨ Shading: PHONG (Smooth)")
                elif event.key == pygame.K_2:                                  # 3.a) GOURAUD SHADING MODEL
                    # 2 = Gouraud shading (flat)
                    obj3d.set_advanced_shading_mode("gouraud")
                    print("🎨 Shading: GOURAUD (Flat)")
                elif event.key == pygame.K_f:
                    # F = Toggle wireframe mode
                    obj3d.wireframe_mode = not obj3d.wireframe_mode
                    print(f"📐 Wireframe: {'ON' if obj3d.wireframe_mode else 'OFF'}")
                elif event.key == pygame.K_r:
                    # R = Toggle auto rotation
                    obj3d.auto_rotate = not obj3d.auto_rotate
                    print(f"🔄 Auto Rotate: {'ON' if obj3d.auto_rotate else 'OFF'}")
                elif event.key == pygame.K_h:
                    # H = Hide/show info panel
                    obj3d.show_info = not obj3d.show_info
                    print(f"📋 Info Display: {'ON' if obj3d.show_info else 'OFF'}")
            elif event.type == pygame.MOUSEBUTTONDOWN:                         # 2) MOUSE DRAG START
                # Mouse click (start dragging)
                if event.button == 1:  # Left mouse button
                    mouse_dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:                           # 2) MOUSE DRAG END
                # Mouse release (stop dragging)
                if event.button == 1:
                    mouse_dragging = False
            elif event.type == pygame.MOUSEMOTION:                             # 2) TRANSFORMASI ROTASI VIA MOUSE
                # Mouse movement (rotation control)
                if mouse_dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - last_mouse_pos[0]  # Delta X
                    dy = mouse_pos[1] - last_mouse_pos[1]  # Delta Y
                    
                    # Convert mouse movement ke rotation (dengan sensitivity)
                    obj3d.target_rotation_y += dx * obj3d.mouse_sensitivity
                    obj3d.target_rotation_x += dy * obj3d.mouse_sensitivity
                    
                    last_mouse_pos = mouse_pos
        
        # Handle continuous keyboard input dengan smooth movement
        keys = pygame.key.get_pressed()  # Get semua key yang sedang ditekan
        if keys[pygame.K_w]:  # W = forward                                    # 2) TRANSFORMASI TRANSLASI VIA KEYBOARD
            obj3d.translation_z += obj3d.movement_speed
        if keys[pygame.K_s]:  # S = backward
            obj3d.translation_z -= obj3d.movement_speed
        if keys[pygame.K_a]:  # A = left
            obj3d.translation_x -= obj3d.movement_speed
        if keys[pygame.K_d]:  # D = right
            obj3d.translation_x += obj3d.movement_speed
        if keys[pygame.K_q]:  # Q = up
            obj3d.translation_y += obj3d.movement_speed
        if keys[pygame.K_e]:  # E = down
            obj3d.translation_y -= obj3d.movement_speed
        
        # Professional rendering pipeline
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Clear screen dan depth buffer
        
        # Animate lighting (cahaya bergerak)
        obj3d.animate_light()
        
        # Apply transformations dan render objek
        obj3d.apply_professional_transformations()                            # 2) APPLY TRANSFORMASI
        obj3d.draw_object()                                                   # 1) RENDER OBJEK 3D
        
        # Render UI overlay (info panel di atas 3D scene)
        ui_surface.fill((0, 0, 0))  # Clear UI surface
        obj3d.render_ui_info(ui_surface, font)
        
        # Convert UI surface ke OpenGL texture dan tampilkan
        # Ini trik untuk overlay 2D UI di atas 3D scene
        ui_data = pygame.image.tostring(ui_surface, 'RGBA', True)
        glWindowPos2f(0, 0)  # Set posisi window
        glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, ui_data)  # Draw UI
        
        pygame.display.flip()  # Swap front/back buffer (double buffering)
        clock.tick(60)  # Maintain 60 FPS
    
    print("👋 Thanks for using Professional 3D Visualization!")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()  # Jalankan program utama
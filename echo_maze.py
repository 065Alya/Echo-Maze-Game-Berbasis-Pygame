# IMPORT LIBRARY

import pygame      # Library utama untuk membuat game (grafik, input, suara)
import sys         # Digunakan untuk keluar dari program (sys.exit)
import math        # Digunakan untuk perhitungan jarak echo (rumus lingkaran)

# INISIALISASI PYGAME & SOUNDS

# Mengatur konfigurasi audio sebelum pygame dijalankan
pygame.mixer.pre_init(44100, -16, 2, 512)

# Mengaktifkan seluruh modul pygame
pygame.init()

# Mengaktifkan modul mixer agar sound bisa dimainkan
pygame.mixer.init()


# Sound saat echo digunakan
echo_sound = pygame.mixer.Sound("echo.mp3")

# Sound saat player menabrak dinding atau gate
hit_sound = pygame.mixer.Sound("hit.mp3")

# Sound saat player berhasil menang
win_sound = pygame.mixer.Sound("win.mp3")

# Sound saat player kalah (game over)
game_over_sound = pygame.mixer.Sound("game_over.mp3")

# Mengatur volume masing-masing sound
echo_sound.set_volume(0.7) #volume diatur 70%
hit_sound.set_volume(0.7) #volume diatur 70%
win_sound.set_volume(0.9) #volume diatur 90%
game_over_sound.set_volume(1) #volume diatur 100%

# KONFIGURASI LAYAR GAME

WIDTH = 800        # Lebar layar (horizontal)
HEIGHT = 600       # Tinggi layar (vertikal)

# Membuat window game
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Judul window
pygame.display.set_caption("Echo Maze - UAS PBO - 065_Alya Khoirun Nur Aini_2024C")

# Membuat objek Clock untuk mengontrol frame rate (FPS) game agar game berjalan dengan kecepatan yang konsisten
clock = pygame.time.Clock()

# DEFINISI WARNA (RGB)
BLACK = (0, 0, 0)         # Warna hitam (background)
WHITE = (255, 255, 255)   # Warna putih (echo & teks)
GRAY  = (120, 120, 120)   # Warna dinding
BLUE  = (0, 120, 255)     # Warna player
RED   = (255, 0, 0)       # Warna gate bergerak
GREEN = (0, 255, 0)       # Warna pintu keluar

# CLASS INDUK (INHERITANCE)

class GameObject:
    """
    Class induk untuk semua objek dalam game.
    Class ini menyimpan posisi x dan y yang akan diwarisi oleh class turunan.
    """

    def __init__(self, x, y):
        # Constructor untuk menginisialisasi posisi objek
        self.x = x          # Posisi horizontal (kiri-kanan) objek 
        self.y = y          # Posisi vertikal (atas - bawah) objek

    def update(self, dt):
        # Method untuk memperbarui state objek setiap frame
        # dt = delta time (waktu yang berlalu sejak frame terakhir)
        # Method ini akan di-OVERRIDE oleh class turunan
        pass

    def draw(self, screen):
        # Method untuk menggambar objek ke layar
        # screen = surface pygame tempat objek digambar
        # Method ini akan di-OVERRIDE oleh class turunan
        pass

# CLASS PLAYER
class Player(GameObject):
    """
    Class Player merupakan Turunan dari GameObject.(Inheritance)
    Class Player mengatur pergerakan pemain,tabrakan, dan jumlah hit.
    """

    def __init__(self, x, y):
        super().__init__(x, y)          # Memanggil constructor GameObject (kelas induk)

        self.size = 20                  # Ukuran kotak player
        self.speed = 150                # Kecepatan gerak player
        # Membuat rectangle untuk collision detection
        self.rect = pygame.Rect(x, y, self.size, self.size) #Rect(x, y, width, height) - posisi dan ukuran player   

        self.hit_count = 0              # Jumlah tabrakan
        self.max_hit = 5                # Batas maksimal tabrakan
        self.hit_cooldown = 0           # Cooldown agar hit tidak berlipat

    def move(self, keys, maze, gates, dt):
        # Method untuk menggerakkan player berdasarkan input keyboard
        # keys = status tombol keyboard yang ditekan
        # maze = objek labirin untuk cek tabrakan dengan dinding
        # gates = list gate bergerak untuk cek tabrakan
        # dt = delta time untuk pergerakan yang smooth
        if self.hit_cooldown > 0: 
            self.hit_cooldown -= dt # --> Mengurangi cooldown hit setiap frame

        # Variabel untuk menyimpan perubahan posisi (delta x, delta y)
        dx, dy = 0, 0  

       # Mengecek tombol panah kiri - gerak ke kiri
        if keys[pygame.K_LEFT]:
            dx = -self.speed * dt    # Negatif = ke kiri (dikali dt agar smooth)
        
        # Mengecek tombol panah kanan - gerak ke kanan
        if keys[pygame.K_RIGHT]:
            dx = self.speed * dt     # Positif = ke kanan
        
        # Mengecek tombol panah atas - gerak ke atas
        if keys[pygame.K_UP]:
            dy = -self.speed * dt    # Negatif = ke atas
        
        # Mengecek tombol panah bawah - gerak ke bawah
        if keys[pygame.K_DOWN]:
            dy = self.speed * dt     # Positif = ke bawah

        # Menyimpan posisi lama (untuk rollback jika tabrakan)
        old_x, old_y = self.rect.x, self.rect.y

        # Gerakan horizontal
        self.rect.x += dx # Tambahkan perubahan posisi horizontal
        # Cek apakah player menabrak dinding ATAU menabrak salah satu gate
        if maze.is_wall(self.rect) or any(g.collide(self.rect) for g in gates):
            self.rect.x = old_x # Kembalikan ke posisi lama (rollback)
            self.handle_hit()   # Proses tabrakan (tambah hit counter + sound)

        # Gerakan vertikal
        self.rect.y += dy    # Tambahkan perubahan posisi vertikal
        # Cek tabrakan vertikal dengan dinding atau gate
        if maze.is_wall(self.rect) or any(g.collide(self.rect) for g in gates):
            self.rect.y = old_y          # Kembalikan ke posisi lama
            self.handle_hit()            # Proses tabrakan

        # Sinkronisasi posisi GameObject dengan posisi rect
        self.x, self.y = self.rect.x, self.rect.y

    def handle_hit(self):  # Method untuk menangani tabrakan player dengan dinding/gate
        # Hit hanya dihitung jika cooldown sudah habis (untuk menghindari double-hit count)
        if self.hit_cooldown <= 0:
            hit_sound.play()            # Mainkan sound tabrakan
            self.hit_count += 1         # Tambah jumlah hit
            self.hit_cooldown = 0.5     # Set cooldown 0.5 detik

    def draw(self, screen):
        # Method untuk menggambar player sebagai kotak biru di layar
        # pygame.draw.rect(surface, color, rect) - gambar rectangle
        pygame.draw.rect(screen, BLUE, self.rect)

# CLASS MAZE (LABIRIN)

class Maze:
    """
    Class Maze menyimpan struktur labirin dalam bentuk grid 2D
    dan mengatur dinding dan pintu keluar, serta mendeteksi tabrakan.
    """

    def __init__(self):                 # Constructor untuk membuat objek maze
        self.tile = 40                  # Ukuran tiap kotak labirin

        # Representasi labirin (1 = dinding, 0 = jalan, E = exit)
        self.grid = [
            "11111111111111111111",
            "10000000000000100001",
            "10111101111110101101",
            "10100001000000100001",
            "10101111011111111001",
            "10001000000000001001",
            "11101111101111101001",
            "10000000001000000001",
            "10111111111001111001",
            "1000000000000011000E",
            "11111111111111111111",
        ]

    def is_wall(self, rect):
        # Method untuk mengecek apakah rect player menyentuh dinding
        # Loop melalui semua pixel di dalam rectangle player
        # Dari top ke bottom dengan langkah sebesar tile
        for y in range(rect.top, rect.bottom, self.tile):
           # Dari left ke right dengan langkah sebesar tile
            for x in range(rect.left, rect.right, self.tile):
                # Konversi koordinat pixel ke koordinat grid
                r = y // self.tile      # Baris (row) dalam grid
                c = x // self.tile      # kolom (coloumn) dalam grid
                if self.grid[r][c] == '1':    # Cek apakah karakter di grid[r][c] adalah '1' (dinding)
                    return True       # Ada tabrakan
        return False # Tidak ada tabrakan

    def is_exit(self, rect):
        # Method untuk mengecek apakah player berada di pintu keluar
        r = rect.centery // self.tile       # Baris dari posisi tengah player
        c = rect.centerx // self.tile       # Kolom dari posisi tengah player
        return self.grid[r][c] == 'E'       # Retrun True jika di pintu keluar atau diposisi 'E'

    def draw(self, screen, echo):
        # Method untuk menggambar dinding hanya jika terkena echo
        for r in range(len(self.grid)):         # Loop melalui setiap baris dalam grid
            for c in range(len(self.grid[r])):  # Loop melalui setiap kolom dalam baris
                x = c * self.tile       # posisi x dalam pixel
                y = r * self.tile       # posisi y dalam pixel

                # Jika karakter di grid adalah '1' (dinding) dan berada dalam radius echo
                if self.grid[r][c] == '1' and echo.visible(x, y, self.tile):
                    # Gambar dinding sebagai kotak abu-abu
                    pygame.draw.rect(screen, GRAY, (x, y, self.tile, self.tile))

                # Jika karakter di grid adalah 'E' (pintu keluar) dan berada dalam radius echo
                if self.grid[r][c] == 'E' and echo.visible(x, y, self.tile):
                    # Gambar pintu keluar sebagai kotak hijau
                    pygame.draw.rect(screen, GREEN, (x, y, self.tile, self.tile))

# CLASS ECHO
class Echo(GameObject):
    """
    Class Echo turunan dari kelas GameObject (INHERITANCE) 
    mewarisi atribute dan method GameObject 
    --> Class ini mengatur sonar pemain yang memungkinkan player melihat labirin
   dalam radius tertentu untuk waktu terbatas.
    """

    def __init__(self, x, y):
        # Memanggil constructor kelas induk GameObject
        super().__init__(x, y)

        self.radius = 0           # Radius echo saat ini (awal = 0)
        self.max_radius = 200     # Radius maksimal echo
        self.active = False       # Status echo (True = aktif atau False = tidak)

        self.max_echo = 5         # Batas maksimal penggunaan echo
        self.echo_used = 0        # Jumlah echo yang sudah digunakan

    def trigger(self, x, y):    # Method untuk mengaktifkan echo pada posisi tertentu
        # Echo hanya bisa dipakai jika belum mencapai batas
        if self.echo_used < self.max_echo:
            self.x, self.y = x, y     # Set posisi echo ke posisi player
            self.radius = 0           # Reset radius echo
            self.active = True        # Aktifkan echo
            self.echo_used += 1       # Tambah jumlah echo yang sudah dipakai
            echo_sound.play()         # Mainkan sound echo

    def update(self, dt):
        # Method memperbarui radius echo setiap frame

        # Jika echo aktif
        if self.active:
            self.radius += 300 * dt   # perbesar radiusnya

            # Jika radius sudah mencapai atau melebihi max_radius
            if self.radius >= self.max_radius:
                self.active = False    # Nonaktifkan echo

    def visible(self, x, y, size):
        # Method untuk mengecek apakah objek berada dalam radius echo
        # Hitung koordinat pusat objek
        cx = x + size / 2     # Koordinat x pusat objek
        cy = y + size / 2     # Koordinat y pusat objek
        # Return True jika echo aktif DAN jarak <= radius
        return self.active and math.hypot(cx - self.x, cy - self.y) <= self.radius

    def draw(self, screen):
        # Method untuk menggambar lingkaran echo
        if self.active:   # Hanya menggambar jika echo aktif
            # pygame.draw.circle(surface, color, center, radius, width)
            # width=1 artinya hanya gambar garis tepi (bukan lingkaran penuh)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(self.radius), 1)

# CLASS MOVING GATE

class MovingGate(GameObject):
    """
    Gate yang muncul (aktif) dan menghilang (inkatif) secara berkala
    untuk menambah tantangan dengan obstacle dinamis.
    """

    def __init__(self, x, y, w, h):
        # Memanggil constructor GameObject
        super().__init__(x, y)
        self.rect = pygame.Rect(x, y, w, h)  # Membuat rectangle untuk posisi dan ukuran gate
        self.timer = 0          # Timer untuk mengatur interval aktif/inaktif
        self.active = True      # Status gate (True = terlihat)

    def update(self, dt):
        # Method untuk memperbarui status gate setiap frame
        self.timer += dt    # Tambah timer dengan delta time
        if self.timer >= 1.2:               # Setiap 1.2 detik
            self.active = not self.active   # Toggle status aktif/inaktif
            self.timer = 0          # Reset timer   

    def collide(self, rect):
        # Method untuk mengecek tabrakan dengan player
        # Return True jika gate aktif dan rect bertabrakan dengan gate
        return self.active and self.rect.colliderect(rect)  

    def draw(self, screen, echo):
        # Method untuk menggambar gate di layar
        # Gambar gate hanya jika aktif DAN terlihat oleh echo
        if self.active and echo.visible(self.rect.x, self.rect.y, self.rect.width):
            # Gambar rectangle merah
            pygame.draw.rect(screen, RED, self.rect)

# CLASS GAME (PENGATUR UTAMA)

class Game:
    """
    Class Game mengatur seluruh alur permainan.
    - Inisialisasi semua objek
    - Game loop (update dan render)
    - Win/lose condition
    - End screen
  
    """

    def __init__(self):
        # Constructor untuk inisialisasi game
        
        # Membuat objek player di posisi (60, 60)
        self.player = Player(60, 60)
        
        # Membuat objek maze
        self.maze = Maze()
        
        # Membuat objek echo di posisi player
        self.echo = Echo(self.player.x, self.player.y)
        
        # Membuat list berisi gate bergerak
        # Saat ini hanya 1 gate di posisi (200, 200) dengan ukuran 40x40
        self.gates = [MovingGate(200, 200, 40, 40)]

        # Status game
        self.running = True             # Game masih berjalan?
        self.win = False                # Player menang?
        self.game_over = False          # Player kalah (game over)?

    def update(self, dt):
        # Method untuk memperbarui state game setiap frame
        
        # Ambil status semua tombol keyboard yang sedang ditekan
        keys = pygame.key.get_pressed()

        # Update player (pergerakan + cek tabrakan)
        self.player.move(keys, self.maze, self.gates, dt)
        
        # Update echo (animasi radius)
        self.echo.update(dt)

        # Update semua gate (timer muncul/hilang)
        for g in self.gates:
            g.update(dt)

        # Cek apakah player sudah sampai di exit
        if self.maze.is_exit(self.player.rect):
            self.win = True             # Player menang
            self.running = False        # Hentikan game loop

        # Cek apakah hit count sudah mencapai maksimal
        if self.player.hit_count >= self.player.max_hit:
            self.game_over = True       # Game over
            self.running = False        # Hentikan game loop

    def draw(self):
        # Method untuk menggambar semua elemen game ke layar
        
        # Isi layar dengan warna hitam (clear screen)
        screen.fill(BLACK)

        # Gambar maze (dinding dan exit)
        self.maze.draw(screen, self.echo)

        # Gambar semua gate
        for g in self.gates:
            g.draw(screen, self.echo)

        # Gambar player (kotak biru)
        self.player.draw(screen)
        
        # Gambar echo (lingkaran putih)
        self.echo.draw(screen)

        # === GAMBAR UI (HIT COUNTER & ECHO COUNTER) ===
        # Buat objek font dengan file custom dan ukuran 25
        font = pygame.font.Font("PixelOperatorSC-Bold.ttf", 25)
        
        # Render teks hit counter (putih)
        # f-string untuk format: "Hits: 3/5" (contoh)
        screen.blit(font.render(f"Hits: {self.player.hit_count}/5", True, WHITE), (10, 10))
        
        # Render teks echo counter (putih)
        # Posisi (10, 30) - di bawah hit counter
        screen.blit(font.render(f"Echo: {self.echo.echo_used}/5", True, WHITE), (10, 30))

    def end_screen(self, text):
        # Method untuk menampilkan layar akhir (win/lose)
        # text = pesan yang akan ditampilkan
        
        # Isi layar dengan hitam
        screen.fill(BLACK)
        
        # Buat font besar untuk pesan akhir
        font = pygame.font.Font("PixelOperatorSC-Bold.ttf", 50)
        
        # Tentukan warna teks: hijau jika menang, merah jika kalah
        text_color = GREEN if self.win else RED
        
        # Render teks dengan warna yang sesuai
        msg = font.render(text, True, text_color)
        
        # Gambar teks di tengah layar
        # get_rect(center=(x, y)) untuk posisikan di tengah
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        
        # Update tampilan layar
        pygame.display.flip()
        
        # Variabel untuk tracking waktu
        start_time = pygame.time.get_ticks()  # Ambil waktu saat ini dalam ms
        timeout = 10000  # 10 detik dalam ms (10 * 1000)
        waiting = True   # Status masih menunggu
        
        # Loop untuk menunggu input ESC atau timeout 10 detik
        while waiting:
            # Hitung waktu yang sudah berlalu sejak end screen muncul
            elapsed_time = pygame.time.get_ticks() - start_time
            
            # Jika sudah lebih dari 10 detik, keluar dari loop
            if elapsed_time >= timeout:
                waiting = False
            
            # Cek semua event yang terjadi
            for event in pygame.event.get():
                # Jika user menutup window (klik X)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Jika user menekan tombol ESC
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False  # Keluar dari loop
            
            # Batas FPS untuk loop ini agar tidak memakan CPU terlalu banyak
            clock.tick(30)

    def run(self):
        # Method utama untuk menjalankan game loop
        
        # Loop utama game - jalan selama self.running = True
        while self.running:
            # clock.tick(60) = batas FPS 60, return ms sejak tick terakhir
            # Dibagi 1000 untuk konversi ms ke detik (dt dalam detik)
            dt = clock.tick(60) / 1000

            # Loop untuk menangani semua event (input, window close, dll)
            for event in pygame.event.get():
                # Jika user menutup window (klik X)
                if event.type == pygame.QUIT:
                    pygame.quit()       # Matikan pygame
                    sys.exit()          # Keluar dari program

                # Jika user menekan tombol E (trigger echo)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    # Aktifkan echo di posisi player saat ini
                    self.echo.trigger(self.player.x, self.player.y)

            # Update state game (pergerakan, collision, win/lose check)
            self.update(dt)
            
            # Gambar semua elemen ke layar
            self.draw()
            
            # Update tampilan layar (swap buffer)
            pygame.display.flip()

        # === SETELAH GAME LOOP SELESAI ===
        # Cek apakah game over atau menang
        
        if self.game_over:
            # Jika game over (terlalu banyak hit)
            game_over_sound.play()      # Mainkan sound game over
            # Tampilkan layar game over
            self.end_screen("GAME OVER - TOO MANY HITS")
        else:
            # Jika menang (sampai exit)
            win_sound.play()            # Mainkan sound kemenangan
            # Tampilkan layar kemenangan
            self.end_screen("YOU ESCAPED THE MAZE!")

# MAIN PROGRAM
if __name__ == "__main__":
    # Cek apakah file ini dijalankan langsung (bukan di-import)
    # Jika ya, jalankan game
    
    # Buat objek Game dan langsung jalankan dengan run()
    Game().run()
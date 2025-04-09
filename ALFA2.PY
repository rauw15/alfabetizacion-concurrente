import tkinter as tk
from tkinter import messagebox
import random
import threading
import queue
from threading import Lock
import time
import pygame
import pyttsx3

class AlphabetHero:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("¡Aventuras con las Letras!")
        self.root.geometry("1024x768")
        pygame.mixer.init()
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        

    
    # Buscar voz en español (generalmente la voz en español tiene 'spanish' en su nombre)
        for voice in voices:
            if 'spanish' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.is_speaking = False 
        
        # Variables del juego
        self.score = 0
        self.coins = 0
        self.current_level = 1
        self.character_selected = None
        self.pets = []
        
        # Variables para concurrencia
        self.score_lock = Lock()
        self.event_queue = queue.Queue()
        self.game_active = threading.Event()
        self.timer_thread = None
        self.animation_thread = None
        self.reward_thread = None
        
        self.setup_main_menu()
        self.start_background_threads()

    def start_background_threads(self):
        """Inicia los hilos en segundo plano"""
        # Hilo del temporizador
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()

        # Hilo de animaciones
        self.animation_thread = threading.Thread(target=self.run_animations, daemon=True)
        self.animation_thread.start()

        # Hilo de recompensas
        self.reward_thread = threading.Thread(target=self.run_rewards, daemon=True)
        self.reward_thread.start()

        # Iniciar el procesador de eventos
        self.root.after(100, self.process_events)

    def run_timer(self):
        """Hilo para manejar el temporizador del juego"""
        while True:
            if self.game_active.is_set():
                time_limit = 30  # Tiempo en segundos
                while time_limit > 0 and self.game_active.is_set():
                    self.event_queue.put(('update_timer', time_limit))
                    time.sleep(1)
                    time_limit -= 1
                if time_limit <= 0:
                    self.event_queue.put(('time_up', None))
            time.sleep(0.1)

    def run_animations(self):
        """Hilo para manejar animaciones"""
        while True:
            if self.game_active.is_set():
                colors = ['#FF4500', '#FF69B4', '#4169E1', '#32CD32', '#FFD700']
                for color in colors:
                    if not self.game_active.is_set():
                        break
                    self.event_queue.put(('animate_color', color))
                    time.sleep(0.5)
            time.sleep(0.1)

    def run_rewards(self):
        """Hilo para manejar recompensas periódicas"""
        while True:
            if self.game_active.is_set():
                time.sleep(60)  # Recompensa cada minuto
                with self.score_lock:
                    self.event_queue.put(('add_reward', 5))
            time.sleep(0.1)

    def process_events(self):
        """Procesa eventos de la cola en el hilo principal"""
        try:
            while True:
                event, data = self.event_queue.get_nowait()
                
                if event == 'update_timer':
                    if hasattr(self, 'timer_label'):
                        self.timer_label.config(text=f"⏱️ Tiempo: {data}s")
                
                elif event == 'time_up':
                    self.game_active.clear()
                    messagebox.showinfo("¡Tiempo!", "¡Se acabó el tiempo!")
                    self.setup_main_menu()
                
                elif event == 'animate_color':
                    if hasattr(self, 'title_label'):
                        self.title_label.config(fg=data)
                
                elif event == 'add_reward':
                    with self.score_lock:
                        self.score += data
                        self.update_status()
                
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_events)

    def setup_main_menu(self):
        # Detener el juego activo
        self.game_active.clear()
        
        # Limpiar pantalla
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Fondo colorido
        self.background = tk.Label(self.root, bg='#FFD700')
        self.background.place(relwidth=1, relheight=1)
        
        # Título animado
        self.title_label = tk.Label(
            self.root,
            text="¡Aventuras con las Letras!",
            font=('Arial', 40, 'bold'),
            fg='#FF4500',
            bg='#FFD700'
        )
        self.title_label.pack(pady=20)
        
        # Selección de personaje
        self.character_frame = tk.Frame(self.root, bg='#FFD700')
        self.character_frame.pack(pady=20)
        
        self.characters = [
            {"name": "Leti la Letra", "color": "#FF69B4"},
            {"name": "Sílabo el Sabio", "color": "#4169E1"},
            {"name": "Voki el Vocabulario", "color": "#32CD32"}
        ]
        
        for char in self.characters:
            self.create_character_button(char)

    def create_character_button(self, character):
        char_btn = tk.Button(
            self.character_frame,
            text=character["name"],
            font=('Arial', 20),
            command=lambda: self.select_character(character),
            bg=character["color"],
            fg='white',
            width=15,
            height=2
        )
        char_btn.pack(pady=10)

    def select_character(self, character):
        self.character_selected = character
        self.show_world_map()

    def show_world_map(self):
        # Limpiar pantalla
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Crear mapa del mundo
        self.world_frame = tk.Frame(self.root, bg='#87CEEB')
        self.world_frame.place(relwidth=1, relheight=1)
        
        # Título del mapa
        tk.Label(
            self.world_frame,
            text="¡Elige tu aventura!",
            font=('Arial', 35, 'bold'),
            bg='#87CEEB',
            fg='white'
        ).pack(pady=20)
        
        # Mundos temáticos
        worlds = [
            {"name": "🏝️ Isla de las Vocales", "level": 1, "color": "#FF69B4"},
            {"name": "🌳 Bosque de las Sílabas", "level": 2, "color": "#32CD32"},
            {"name": "🏙️ Ciudad de las Palabras", "level": 3, "color": "#4169E1"}
        ]
        
        for world in worlds:
            self.create_world_button(world)

    def create_world_button(self, world):
        world_btn = tk.Button(
            self.world_frame,
            text=world["name"],
            font=('Arial', 25),
            command=lambda: self.start_world(world),
            bg=world["color"],
            fg='white',
            width=20,
            height=2
        )
        world_btn.pack(pady=20)

    def start_world(self, world):
        self.current_world = world
        self.setup_game_level()

    def setup_game_level(self):
        # Limpiar pantalla
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configurar nivel de juego
        self.game_frame = tk.Frame(self.root, bg='#E0FFFF')
        self.game_frame.place(relwidth=1, relheight=1)
        
        # Barra de estado
        self.status_bar = tk.Frame(self.game_frame, bg='#4169E1')
        self.status_bar.pack(fill=tk.X)
        
        # Timer label
        self.timer_label = tk.Label(
            self.status_bar,
            text="⏱️ Tiempo: 30s",
            font=('Arial', 20),
            bg='#4169E1',
            fg='white'
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)
        
        # Mostrar puntuación y monedas
        self.score_label = tk.Label(
            self.status_bar,
            text=f"⭐ Puntos: {self.score}",
            font=('Arial', 20),
            bg='#4169E1',
            fg='white'
        )
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.coins_label = tk.Label(
            self.status_bar,
            text=f"🪙 Monedas: {self.coins}",
            font=('Arial', 20),
            bg='#4169E1',
            fg='white'
        )
        self.coins_label.pack(side=tk.RIGHT, padx=10)
        
        # Botón de regreso
        tk.Button(
            self.status_bar,
            text="🏠 Menú",
            font=('Arial', 15),
            command=self.setup_main_menu,
            bg='#FF69B4',
            fg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        # Área de juego
        self.play_area = tk.Frame(self.game_frame, bg='#E0FFFF')
        self.play_area.pack(expand=True, fill=tk.BOTH, pady=20)
        
        # Activar el juego y comenzar
        self.game_active.set()
        self.start_mini_game()

    def start_mini_game(self):
        if self.current_world["level"] == 1:
            self.vowel_game()
        elif self.current_world["level"] == 2:
            self.syllable_game()
        else:
            self.word_game()

    def clear_play_area(self):
        for widget in self.play_area.winfo_children():
            widget.destroy()

    def clear_play_area(self):
        for widget in self.play_area.winfo_children():
            widget.destroy()

    def vowel_game(self):
        self.clear_play_area()
        
        vowels = ['A', 'E', 'I', 'O', 'U']
        self.current_vowel = random.choice(vowels)
        
        label = tk.Label(
            self.play_area,
            text=f"¡Encuentra la vocal {self.current_vowel}!",
            font=('Arial', 30),
            bg='#E0FFFF'
        )
        label.pack(pady=20)
        label.bind("<Enter>", lambda event: self.delayed_play_vowel_sound(self.current_vowel))
        balloon_frame = tk.Frame(self.play_area, bg='#E0FFFF')
        balloon_frame.pack(expand=True)
        
        random.shuffle(vowels)
        for vowel in vowels:
            self.create_balloon(balloon_frame, vowel)

    def play_vowel_sound(self, letter):
        try:
            if pygame.mixer.music.get_busy():
                return
            pygame.mixer.music.load(f"./audios/vowel_game{letter.lower()}.wav")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error al reproducir el sonido: {e}")

    def delayed_play_vowel_sound(self, letter):
        # Agrega un retraso de 0.5 segundos antes de reproducir el sonido
        self.root.after(500, self.play_vowel_sound, letter)     

    def create_balloon(self, parent, letter):
        colors = ['#FF69B4', '#FF6347', '#4169E1', '#32CD32', '#FFD700']
        btn = tk.Button(
            parent,
            text=letter,
            font=('Arial', 40),
            bg=random.choice(colors),
            fg='white',
            width=3,
            command=lambda: self.check_vowel(letter)
        )
        btn.pack(side=tk.LEFT, padx=20)
        btn.bind("<Enter>", lambda event, ltr=letter: self.play_vowel_Vocal(ltr))

    def play_vowel_Vocal(self, letter):
        try:
            
            pygame.mixer.music.load(f"./audios/{letter.lower()}.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error al reproducir el sonido: {e}")


    def check_vowel(self, selected_vowel):
        if selected_vowel == self.current_vowel:
            with self.score_lock:
                self.score += 10
                self.coins += 1
                self.update_status()
            messagebox.showinfo("¡Correcto! 🎉", "¡Muy bien! ¡Ganaste una moneda! 🪙")
            self.vowel_game()
        else:
            messagebox.showinfo("¡Inténtalo de nuevo! 💪", "¡Tú puedes!")

    def syllable_game(self):
        self.clear_play_area()
        
        syllables = ['MA', 'ME', 'MI', 'MO', 'MU', 'PA', 'PE', 'PI', 'PO', 'PU']
        self.current_syllable = random.choice(syllables)
        
        label=tk.Label(
            self.play_area,
            text=f"¡Encuentra la sílaba {self.current_syllable}!",
            font=('Arial', 30),
            bg='#E0FFFF'
        )
        label.pack(pady=20)
        label.bind("<Enter>", lambda event: self.delayed_play_syllable_sound(self.current_syllable))
        
        syllable_frame = tk.Frame(self.play_area, bg='#E0FFFF')
        syllable_frame.pack(expand=True)
        
        available_syllables = [s for s in syllables if s != self.current_syllable]
        random.shuffle(available_syllables)
        game_syllables = available_syllables[:4] + [self.current_syllable]
        random.shuffle(game_syllables)
        
        for syllable in game_syllables:
            self.create_syllable_button(syllable_frame, syllable)

    def delayed_play_syllable_sound(self, letter):
        # Agrega un retraso de 0.5 segundos antes de reproducir el sonido
        self.root.after(500, self.play_syllable_sound, letter) 

    def play_syllable_sound(self, letter):
        try:
            if pygame.mixer.music.get_busy():
                return
            pygame.mixer.music.load(f"./audios/syllable_game{letter.lower()}.wav")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error al reproducir el sonido: {e}")



    def create_syllable_button(self, parent, syllable):
        colors = ['#FF69B4', '#FF6347', '#4169E1', '#32CD32', '#FFD700']
        btn = tk.Button(
            parent,
            text=syllable,
            font=('Arial', 30),
            bg=random.choice(colors),
            fg='white',
            width=4,
            command=lambda: self.check_syllable(syllable)
        )
        btn.pack(side=tk.LEFT, padx=10)
        btn.bind("<Enter>", lambda event, ltr=syllable: self.play_syllable_Vocal(ltr))

    def play_syllable_Vocal(self, syllable):
        try:
            
            pygame.mixer.music.load(f"./audios/{syllable.lower()}.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error al reproducir el sonido: {e}")


    def check_syllable(self, selected_syllable):
        if selected_syllable == self.current_syllable:
            with self.score_lock:
                self.score += 20
                self.coins += 2
                self.update_status()
            messagebox.showinfo("¡Correcto! 🎉", "¡Excelente! ¡Ganaste 2 monedas! 🪙🪙")
            self.syllable_game()
        else:
            messagebox.showinfo("¡Inténtalo de nuevo! 💪", "¡Sigue intentando!")

    def word_game(self):
        self.clear_play_area()
        
        words = {
            'CASA': 'Lugar donde vivimos',
            'MESA': 'Mueble con cuatro patas',
            'SOPA': 'Comida caliente con líquido',
            'PATO': 'Ave que nada en el agua',
            'LUNA': 'Brilla en el cielo de noche'
        }
        
        self.current_word = random.choice(list(words.keys()))
        self.word_display = ["_"] * len(self.current_word)
        
        label1=tk.Label(
            self.play_area,
            text="¡Forma la palabra!",
            font=('Arial', 30),
            bg='#E0FFFF'
        )
        label1.pack(pady=10)
        label1.bind("<Enter>", self.speak_widget_text)
        
        label2=tk.Label(
            self.play_area,
            text=f"Pista: {words[self.current_word]}",
            font=('Arial', 25),
            bg='#E0FFFF',
            wraplength=600
        )
        label2.pack(pady=10)
        label2.bind("<Enter>", self.speak_widget_text)
        
        tk.Label(
            self.play_area,
            text=f"La palabra tiene {len(self.current_word)} letras:",
            font=('Arial', 20),
            bg='#E0FFFF'
        ).pack(pady=10)
        
        self.word_display_label = tk.Label(
            self.play_area,
            text=" ".join(self.word_display),
            font=('Arial', 40),
            bg='#E0FFFF'
        )
        self.word_display_label.pack(pady=10)
        
        tk.Label(
            self.play_area,
            text=f"Comienza con '{self.current_word[0]}' y termina con '{self.current_word[-1]}'",
            font=('Arial', 20),
            bg='#E0FFFF'
        ).pack(pady=10)
        
        self.word_entry = tk.Entry(
            self.play_area,
            font=('Arial', 30),
            width=10
        )
        self.word_entry.pack(pady=20)
        
        # Vincular el evento de tecla presionada
        self.word_entry.bind('<KeyRelease>', self.check_letter)
        
        button_frame = tk.Frame(self.play_area, bg='#E0FFFF')
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Comprobar Palabra",
            font=('Arial', 20),
            command=self.check_word,
            bg='#32CD32',
            fg='white'
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="🔍 Pista",
            font=('Arial', 20),
            command=self.give_hint,
            bg='#4169E1',
            fg='white'
        ).pack(side=tk.LEFT, padx=10)
        
    def speak_widget_text(self, event):
        widget = event.widget
        text = widget.cget("text")  # Accede al texto del widget
        
        if self.is_speaking:
            self.engine.stop()  # Detener el audio actual si ya está hablando
            self.is_speaking = False  # Reiniciar la bandera

        # Reproducir el nuevo texto
        self.engine.say(text)
        self.engine.runAndWait()  # Espera hasta que termine de hablar
        self.is_speaking = True  # Marcar que ahora está hablando

    def check_letter(self, event):
        current_text = self.word_entry.get().upper()
        if current_text:
            if len(current_text) <= len(self.current_word):
                correct_so_far = True
                for i, letter in enumerate(current_text):
                    if i < len(self.current_word):
                        if letter != self.current_word[i]:
                            correct_so_far = False
                            self.hint_label.config(
                                text=f"❌ La letra '{letter}' no va en esa posición",
                                fg='#FF4500'
                            )
                            break
                
                if correct_so_far:
                    self.hint_label.config(
                        text="✅ ¡Vas bien! Sigue escribiendo...",
                        fg='#32CD32'
                    )
                    
                    for i, letter in enumerate(current_text):
                        self.word_display[i] = letter
                    self.word_display_label.config(text=" ".join(self.word_display))
            else:
                self.hint_label.config(
                    text="❌ ¡Demasiadas letras!",
                    fg='#FF4500'
                )

    def give_hint(self):
        hidden_indices = [i for i, letter in enumerate(self.word_display) if letter == "_"]
        if hidden_indices:
            hint_index = random.choice(hidden_indices)
            self.word_display[hint_index] = self.current_word[hint_index]
            self.word_display_label.config(text=" ".join(self.word_display))
            with self.score_lock:
                self.score -= 5
                self.update_status()
        else:
            messagebox.showinfo("Pistas", "¡Ya se han revelado todas las letras!")

    def check_word(self):
        answer = self.word_entry.get().upper()
        if answer == self.current_word:
            with self.score_lock:
                self.score += 30
                self.coins += 3
                self.update_status()
            messagebox.showinfo("¡Correcto! 🎉", 
                              f"¡Fantástico! La palabra era {self.current_word}.\n¡Ganaste 3 monedas! 🪙🪙🪙")
            self.word_entry.delete(0, tk.END)
            self.word_game()
        else:
            messagebox.showinfo("¡Inténtalo de nuevo! 💪", 
                              f"Esa no es la palabra.\nRecuerda que tiene {len(self.current_word)} letras.")

    def update_status(self):
        self.score_label.config(text=f"⭐ Puntos: {self.score}")
        self.coins_label.config(text=f"🪙 Monedas: {self.coins}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = AlphabetHero()
    game.run()
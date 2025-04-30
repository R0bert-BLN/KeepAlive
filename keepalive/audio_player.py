import pygame

is_mixer_active = False

def start_mixer():
    global is_mixer_active
    
    if is_mixer_active:
        return True
    
    try:
        pygame.mixer.init()
        is_mixer_active = True
        
        print("INFO: pygame.mixer started")
        return True
    except pygame.error as e:
        print(f"ERROR: Error starting pygame.mixer: {e}")
        return False

def stop_mixer():
    global is_mixer_active
    
    if is_mixer_active:
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            
            pygame.mixer.quit()
            is_mixer_active = False
            
            print("INFO: pygame.mixer stopped")
        except pygame.error as e:
            print(f"ERROR: Error stopping pygame.mixer: {e}")

def play_sound(sound_file_path, volume):
    global is_mixer_active
    
    if not is_mixer_active:
        print("ERROR: pygame.mixer is not active")
        return False
    
    try:
        pygame.mixer.music.load(sound_file_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()
        
        print(f"INFO: Playing {sound_file_path}")
        return True
    except pygame.error as e:
        print(f"ERROR: Error playing {sound_file_path}: {e}")
        return False

def is_busy():
    if is_mixer_active:
        return pygame.mixer.music.get_busy()
    else:
        return False

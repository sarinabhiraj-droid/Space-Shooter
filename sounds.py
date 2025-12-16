import pygame

pygame.mixer.init()

shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
powerup_sound = pygame.mixer.Sound("sounds/powerup.wav")
game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")

shoot_sound.set_volume(0.4)
explosion_sound.set_volume(0.6)
powerup_sound.set_volume(0.5)
game_over_sound.set_volume(0.7)

pygame.mixer.music.load("sounds/bg_music.wav")
pygame.mixer.music.set_volume(0.3)

def play_music():
    pygame.mixer.music.play(-1)

def stop_music():
    pygame.mixer.music.stop()

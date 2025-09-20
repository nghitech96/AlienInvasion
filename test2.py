import pygame

pygame.init()

# Tạo nhóm bullets và aliens
bullets = pygame.sprite.Group()
aliens = pygame.sprite.Group()

# Định nghĩa class Bullet và Alien
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(topleft=(x, y))

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

# Thêm 1 viên đạn và 1 alien
bullets.add(Bullet(50, 50))
aliens.add(Alien(50, 50))  # Trùng vị trí => sẽ va chạm

# Kiểm tra va chạm
collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
print("Collisions:", collisions)

if collisions:
    print("DEBUG: Có một viên đạn trúng alien!")
    print("DEBUG: Số lượng alien còn lại:", len(aliens))
else:
    print("DEBUG: Không có va chạm!")

pygame.quit()

import sys
import pygame
from settings import Settings
from ship import Ship
from alien import Alien
from bullet import Bullet
from time import sleep
from game_stats import GameStats
from button import Button
from Scoreboard import Scoreboard

class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )

        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height

        #Set background color
        self.bg_color = (255, 0, 255)
        pygame.display.set_caption("Alien Invasion")

        #The ship
        self.ship = Ship(self)
        #self.ship = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        print("DEBUG: Gọi hàm _create_fleet()")

        self._create_fleet()
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.play_button = Button(self, "Play")

    def _create_fleet(self):
        """Create the fleet of aliens."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = self.settings.screen_height - (3 * alien_height) - ship_height
        number_rows = available_space_y // (2 * alien_height)

        print(f"Tạo {number_rows} hàng, mỗi hàng {number_aliens_x} alien")

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                alien = Alien(self)
                self._create_alien(alien_number, row_number)
                alien_width = alien.rect.width
                alien.x = alien_width + 2 * alien_width * alien_number
                alien.rect.x = alien.x
                self.aliens.add(alien)

        print("DEBUG: Tổng số Alien sau khi tạo =", len(self.aliens))
        print("DEBUG INFO:")
        print("alien_width:", alien_width, "alien_height:", alien_height)
        print("available_space_x:", available_space_x, "available_space_y:", available_space_y)
        print("number_aliens_x:", number_aliens_x, "number_rows:", number_rows)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number

        self.aliens.add(alien)


    def _fire_bullet(self):
        new_bullet = Bullet(self)
        self.bullets.add(new_bullet)

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        print("Số lượng Alien:", len(self.aliens))
        # Erase the old screen
        self.screen.fill(self.settings.bg_color)
        # Draw the bullets
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        # Draw the ship
        self.ship.blitme()
        # Draw alien
        self.aliens.draw(self.screen)
        self.sb.show_score()

        if not self.stats.game_active:
            self.play_button.draw_button()
        # Display new screen
        pygame.display.flip()


    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_events(self):
        for event in pygame.event.get():
            print(event)  # DEBUG: Print all the events

            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                print("KEYDOWN:", event.key)  # Print out key code
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                print("KEYUP:", event.key)
                self._check_keyup_events(event)

            mouse_pos = pygame.mouse.get_pos()
            self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        """Start a new game when the player clicks Play."""
        if button_clicked and not self.stats.game_active:
           # Reset the game settings.
           self.settings.initialize_dynamic_settings()

           # Reset the game statistics.
           self.stats.reset_stats()
           self.stats.game_active = True
           self.sb.prep_score()
           self.sb.prep_level()

           # Get rid of any remaining aliens and bullets.
           self.aliens.empty()
           self.bullets.empty()

           # Create a new fleet and center the ship.
           self._create_fleet()
           self.ship.center_ship()

           # Hide the mouse cursor.
           pygame.mouse.set_visible(False)

           button_clicked = self.play_button.rect.collidepoint(mouse_pos)
           if button_clicked and not self.stats.game_active:
               # Reset the game statistics.
               self.stats.reset_stats()
               self.stats.game_active = True

               # Get rid of any remaining aliens and bullets.
               self.aliens.empty()
               self.bullets.empty()

               # Create a new fleet and center the ship.
               self._create_fleet()
               self.ship.center_ship()

               # Hide the mouse cursor.
               pygame.mouse.set_visible(False)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions
        self.bullets.update()

        # Remove bullets that have disappeared
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        #Check for any bullets that have hit aliens.
        #If so, get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self.sb.prep_high_score()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(collisions)
                self.sb.prep_score()
                self.sb.check_high_score()

    def _update_aliens(self):
        """Check if the fleet is at an edge,
           then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def run_game(self):
        """Start the main loop for the game."""
        """ pygame.QUIT event means the user clicked X to close your window """
        clock = pygame.time.Clock()

        while True:
            self._check_events()
            self._update_screen()# Executive event
            self.ship.update()        # Update ship

            for bullet in self.bullets.copy():
                if bullet.rect.bottom <= 0:
                    self.bullets.remove(bullet)
                print(len(self.bullets))
            self.bullets.update()
            self._update_bullets()
            self._update_aliens()
             # Redraw the screen during each pass through the loop
             # Make the most recently drawn screen visible.
            self._update_screen()
            self.aliens.update()
            clock.tick(60)

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()

import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from npc import Npc
from menu import Menu
from dialog import Dialog_box
from save_and_load import found_save_or_not

class Level:
    def __init__(self):
        # get the display surface
        
        self.game_paused = False
        
        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # dialog
        self.dialog = Dialog_box()

        # sprite setup
        self.create_map()
        
        # save
        self.has_save = False
        found_save_or_not(self)

        # user interface
        self.menu_state = 'none'
        self.menu = Menu(self)
        self.prev_menu_state = 'none'
        self.menu_list = self.menu.button_names


    def create_map(self):
        # map system
        layouts = {
            'boundary' : import_csv_layout('assets/map/test_map_border.csv'),
            'entities': import_csv_layout('assets/map/test_map_entity.csv')
        }
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        # boundary blocks
                        if style == 'boundary':
                            Tile(
                                (x, y), 
                                [self.obstacle_sprites,
                                # self.visible_sprites
                                ], 
                                'invisible'
                                )
                        if style == 'entities':
                            # create entities
                            if col == '394':
                                # player_id in tile_map
                                self.player = Player(
                                    (x, y),
                                    [self.visible_sprites], 
                                    self.obstacle_sprites,
                                    )
                            elif col == '395':
                                self.npc = Npc('test', 
                                    (x, y), 
                                    [
                                        self.visible_sprites,
                                        self.obstacle_sprites
                                    ], 
                                    self.obstacle_sprites,
                                    self.dialog
                                    )

    def player_dead(self):
        # perform player dead react
        # if player dead player's exp left half
        left_exp = self.player.exp/2
        left_stats = self.player.stats
        left_mex_stats = self.player.max_stats
        left_upgrade_cost = self.player.upgrade_cost
        self.__init__()
        self.player.exp = left_exp
        self.player.stats = left_stats
        self.player.max_stats = left_mex_stats
        self.player.upgrade_cost = left_upgrade_cost
        self.player.speed = self.player.stats['speed']
        self.player.refresh_stats()

    def toggle_menu(self):
        self.game_paused = not(self.game_paused)

    def title_screen(self):
        self.prev_menu_state = self.menu_state
        if self.menu_state != 'menu' or self.menu_state != 'title' or self.menu_state != 'dead_screen':
            self.toggle_menu()
            self.menu_state = 'menu'
        elif self.menu_state == 'menu' or self.menu_state == 'title' or self.menu_state == 'dead_screen':
            self.toggle_menu()
            self.menu_state  = 'none'

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        if self.game_paused:
            # menu system showed
            if self.menu_state == 'title' or self.menu_state == 'menu' or self.menu_state == 'dead_screen':
                self.menu.display()
        else:
            if self.menu_state != 'none':
                self.menu_state = 'none'
            # run the game
            # update and draw the game
            self.visible_sprites.update()
            self.visible_sprites.npc_update(self.player)
            crt_shader()

class YSortCameraGroup(pygame.sprite.Group):
    # in godot we call it YSort to make 2.5D
    def __init__(self):
        # general setup
        super().__init__()

        # camera offset
        self.offset = pygame.math.Vector2()
        # to stay player in middle of screen. cut it half.
        self.half_screen_width = screen.get_size()[0]//2
        self.half_screen_height = screen.get_size()[1]//2
        # //2 to get divide 2 result in int

        # box camera setup
        # self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
        self.camera_borders = {'left': 400, 'right': 400, 'top': 200, 'bottom': 200}
        camera_boarders_left = self.camera_borders['left']
        camera_boarders_top = self.camera_borders['top']
        camera_boarders_width = screen.get_size()[0]  - (self.camera_borders['left'] + self.camera_borders['right'])
        camera_boarders_height = screen.get_size()[1]  - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(camera_boarders_left, camera_boarders_top, camera_boarders_width, camera_boarders_height)

        # creating the floor/ground
        self.floor_surf = pygame.image.load(resource_path('assets/graphics/tilemap/bg.png')).convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (0, 0))

        # camera speed
        self.keyboard_speed = 5
        self.mouse_speed = 0.4

        # zoom
        self.zoom_scale = 1
        # don't set too large would be lag
        self.internal_surface_size = (WIDTH * 1.5, HEIGHT * 1.5)
        self.internal_surface = pygame.Surface(self.internal_surface_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surface.get_rect(center = (self.half_screen_width, self.half_screen_height))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surface_size)
        self.internal_offset = pygame.math.Vector2() # need to add after all offset: ground and every object
        self.internal_offset.x = self.internal_surface_size[0] // 2 - self.half_screen_width
        self.internal_offset.y = self.internal_surface_size[1] // 2 - self.half_screen_height

        self.zoom_scale_mininum = WIDTH/self.internal_surface_size[0] # change to large scale
        self.zoom_scale_maxinum = self.internal_surface_size[0]/WIDTH
        # self.zoom_scale_mininum = 0.5 # change to large scale
        # self.zoom_scale_maxinum = 2

    def center_target_camera(self, target):
        # put target at camera center
        # self.offset.x = player.rect.centerx - self.half_screen_width
        # self.offset.y = player.rect.centery - self.half_screen_height
        self.offset.x = target.rect.centerx - self.half_screen_width
        self.offset.y = target.rect.centery - self.half_screen_height

    def box_target_camera(self, target):
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def keyboard_control_camera(self):
        keys = pygame.key.get_pressed()
        # ver 1 only for keyboard
        # if keys[pygame.K_a]:self.offset.x -= self.keyboard_speed
        # if keys[pygame.K_d]:self.offset.x += self.keyboard_speed
        # if keys[pygame.K_w]:self.offset.y -= self.keyboard_speed
        # if keys[pygame.K_s]:self.offset.y += self.keyboard_speed
            
        # ver 2 for keyboard and camera box
        if keys[pygame.K_a]:self.camera_rect.x -= self.keyboard_speed
        if keys[pygame.K_d]:self.camera_rect.x += self.keyboard_speed
        if keys[pygame.K_w]:self.camera_rect.y -= self.keyboard_speed
        if keys[pygame.K_s]:self.camera_rect.y += self.keyboard_speed
        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def mouse_control_camera(self):
        # mouse setting
        pygame.event.set_grab(True) # make mouse can't leave screen anymore
        mouse = pygame.math.Vector2(pygame.mouse.get_pos())
        mouse_offset_vector = pygame.math.Vector2()

        left_border = self.camera_borders['left']
        top_border = self.camera_borders['top']
        right_border = screen.get_size()[0] - self.camera_borders['right']
        bottom_border = screen.get_size()[1] - self.camera_borders['bottom']

        if top_border < mouse.y < bottom_border:
            if mouse.x < left_border:
                mouse_offset_vector.x = mouse.x - left_border
                pygame.mouse.set_pos((left_border, mouse.y))
            if mouse.x > right_border:
                mouse_offset_vector.x = mouse.x - right_border
                pygame.mouse.set_pos((right_border, mouse.y))
        elif mouse.y < top_border:
            if mouse.x < left_border:
                mouse_offset_vector = mouse - pygame.math.Vector2(left_border, top_border)
                pygame.mouse.set_pos((left_border, top_border))
            if mouse.x > right_border:
                mouse_offset_vector = mouse - pygame.math.Vector2(right_border, top_border)
                pygame.mouse.set_pos((right_border, top_border))
        elif mouse.y > bottom_border:
            if mouse.x < left_border:
                mouse_offset_vector = mouse - pygame.math.Vector2(left_border, bottom_border)
                pygame.mouse.set_pos((left_border, bottom_border))
            if mouse.x > right_border:
                mouse_offset_vector = mouse - pygame.math.Vector2(right_border, bottom_border)
                pygame.mouse.set_pos((right_border, bottom_border))

        if left_border < mouse.x < right_border:
            if mouse.y < top_border:
                mouse_offset_vector.y = mouse.y - top_border
                pygame.mouse.set_pos((mouse.x, top_border))
            if mouse.y > bottom_border:
                mouse_offset_vector.y = mouse.y - bottom_border
                pygame.mouse.set_pos((mouse.x, bottom_border))

        # self.offset += mouse_offset_vector * self.mouse_speed # ver 1 for only mouse
        self.camera_rect.x += mouse_offset_vector.x * self.mouse_speed
        self.camera_rect.y += mouse_offset_vector.y * self.mouse_speed

    def zoom_keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_EQUALS]:
            self.zoom_scale += 0.1
        if keys[pygame.K_MINUS]:
            self.zoom_scale -= 0.1
        if keys[pygame.K_0]:
            self.zoom_scale = 1

    def custom_draw(self, player):
        # getting the offset
        # self.center_target_camera(player) # center camera
        self.box_target_camera(player) # camera box
        self.keyboard_control_camera()
        self.zoom_keyboard_control()
        # self.mouse_control_camera()

        # limit scale size
        if self.zoom_scale < self.zoom_scale_mininum:
            self.zoom_scale = self.zoom_scale_mininum
        elif self.zoom_scale > self.zoom_scale_maxinum:
            self.zoom_scale = self.zoom_scale_maxinum

        self.internal_surface.fill('black')
        
        # drawing the floor
        # offset needed
        floor_offset_pos = self.floor_rect.topleft - self.offset + self.internal_offset
        # screen.blit(self.floor_surf, floor_offset_pos)
        self.internal_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            # use sort to create the YSort. and now it has overlap.
            # for camera sprite.rect need to add a offset. 
            # and offset comes from player
            # offset needed
            offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
            # to make camera direction right need to subtract offset
            # screen.blit(sprite.image, offset_pos)
            self.internal_surface.blit(sprite.image, offset_pos)

        scaled_surf  = pygame.transform.scale(self.internal_surface, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center = (self.half_screen_width, self.half_screen_height))

        screen.blit(scaled_surf, scaled_rect)
        
        # camera box line
        # pygame.draw.rect(screen, 'yellow', self.camera_rect, 5)

    def npc_update(self, player):
        npc_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'npc']
        for npc in npc_sprites:
            npc.npc_update(player)

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from settings import *
from save_and_load import save_dialogue, load_dialogue
import re

class Gui_helper:
    def __init__(self, game):
        # tkinter frame
        self.game = game
        self.root= Tk()
        self.root.iconbitmap(resource_path('assets/graphics/icon/icon.ico'))
        self.root.title('Line editor')
        self.root.geometry('380x300')
        # line list box
        self.character_select = Combobox(self.root, width=10)
        self.character_select.grid(column=0, row=0, sticky=N)
        self.character_select['values'] = ['npc']
        self.character_select.current(0)
        self.textlistbox = Listbox(self.root, height=6)
        self.init_textlist()
        self.textlistbox.grid(column=0, row=1, padx=10, rowspan=6, sticky=N+W)
        # line input
        self.linetext = Label(self.root,text='Input Line :')
        self.linetext.grid(column=1, row=0, sticky=N + W)
        self.lineinput = Entry(self.root,width=25)
        self.lineinput.grid(column=1, row=1, columnspan=3, sticky=N)
        # buttons
        self.edit_line_btn = Button(self.root, text='edit line', command=self.edit_line)
        self.edit_line_btn.grid(column=1, row=2, sticky=W)
        self.confirm_line_btn = Button(self.root, text='add line', command=self.add_line)
        self.confirm_line_btn.grid(column=2, row=2,sticky=W)
        self.save_line_btn = Button(self.root, text='save file', command=self.save_lines)
        self.save_line_btn.grid(column=1, row=3, sticky=W)
        self.load_line_btn = Button(self.root, text='load file', command=self.load_lines)
        self.load_line_btn.grid(column=2, row = 3, sticky=W)

        global load_file_name
        load_file_name = StringVar()
        load_file_name.set('none')
        # save section
        self.linetext = Label(self.root,text='file name + format:')
        self.linetext.grid(column=1, row=4, sticky=N + W)
        self.file_name_input = Entry(self.root,width=10)
        self.file_name_input.grid(column=1, row=5, columnspan=3, sticky=N+W)
        self.file_format_input = Entry(self.root,width=10)
        self.file_format_input.grid(column=2, row=5, columnspan=3, sticky=N+W)
        self.now_file_hint = Label(self.root, text='now file:')
        self.now_file_hint.grid(column=1, row=6, sticky=N+E)
        self.now_file_name = Label(self.root, textvariable=load_file_name)
        self.now_file_name.grid(column=2, row=6, sticky=N+W)

        # image edit
        self.img_hint = Label(self.root, text='image select')
        self.img_hint.grid(column=0, row=6, sticky=S+W)
        self.img_select_box = Combobox(self.root, width=10)
        self.img_select_box.grid(column=0, row=7, sticky=S+W)
        self.img_select_box['values'] = ['bg','player walk img', 'npc walk img', 'npc talk img']
        self.img_select_box.current(0)
        self.edit_img_btn = Button(self.root, text='edit img', command=self.edit_img)
        self.edit_img_btn.grid(column=0, row=8, sticky=W+N)

    def init_textlist(self):
        # clear text list first
        self.textlistbox.delete(0, END)
        # then insert all the lines
        for line in npc_lines_all:
            self.textlistbox.insert(END, line)

    def edit_line(self):
        list_chose = self.textlistbox.curselection()
        line = self.lineinput.get()
        if len(list_chose) > 0:
            if line:
                npc_lines_all[list_chose[0]] = line
            else:
                del npc_lines_all[list_chose[0]]
            self.init_textlist()
        else:
            self.init_textlist()

    def add_line(self):
        line = self.lineinput.get()
        if line:
            if line.isspace():
                self.init_textlist()
            else:
                self.textlistbox.insert(END, line)
                npc_lines_all.append(line)

    def save_lines(self):
        global load_file_name
        file_name = self.file_name_input.get()
        file_format = self.file_format_input.get()
        if file_name:
            if not(file_format):
                file_format = '.dialogue'
            if not('.' in file_format):
                file_format = '.' + file_format
            load_file_name.set(file_name)
            path = './' + file_name + file_format
            save_dialogue(path, npc_lines_all)

    def load_lines(self):
        # npc_lines_all = load_dialogue()
        # print(npc_lines_all)
        dialogue_path = filedialog.askopenfilename()
        if dialogue_path:
            # print(dialogue_path)
            file_name = re.split('/|\.', dialogue_path)[-2]
            # re module split multi diagram. '.' is special character need slash.
            global load_file_name
            load_file_name.set(file_name)
            lines = load_dialogue(dialogue_path)
            npc_lines_all.clear()
            for line in lines:
                npc_lines_all.append(line)
            self.init_textlist()

    def edit_img(self):
        img_path = filedialog.askopenfilename()
        # if 'png' in img_path:
        if img_path:
            load_img = pygame.image.load(resource_path(img_path))
            select_img = self.img_select_box.get()
            if select_img == 'bg':
                self.game.level.visible_sprites.floor_surf = load_img
            elif select_img == 'player walk img':
                self.game.level.player.image = pygame.transform.scale(load_img,(TILESIZE, TILESIZE))
            elif select_img == 'npc walk img':
                self.game.level.npc.or_image = pygame.transform.scale(load_img,(TILESIZE, TILESIZE))
                self.game.level.npc.image = self.game.level.npc.or_image.copy()
            elif select_img == 'npc talk img':
                self.game.level.dialog.talker_image = pygame.transform.scale(load_img,(152, 152))

    def run(self):
        self.root.mainloop()
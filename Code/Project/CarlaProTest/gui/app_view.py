import tkinter as tk
import time

from tkinter import ttk
from PIL import Image, ImageTk
from threading import Thread
from queue import Queue

from model.image_processing import CustomCarlaDataset

OBJ_ID = 'Object id'
OBJ_TYP = 'Object typ'


class MainApp(object):

    def __init__(self):
        print("Main class")
        self.main_window = tk.Tk()
        self.main_window.title("Project 2: WiSo19/20")
        self.main_window.geometry('1267x914')

        im_lst, json_lst = CustomCarlaDataset.load()
        self.main_panel = MainPanel(self.main_window, len(im_lst))
        print(len(im_lst), len(json_lst))
        print(type(im_lst))


#########################################################
#              Layout of the application                #
#########################################################

class MainPanel(object):

    def __init__(self, master, max_length):
        # main frame
        root_panel = ttk.Frame(master)
        root_panel.pack()

        # create panels for control and visualization
        # top container of control panel
        self.frame_control = ttk.Frame(root_panel)
        self.frame_control.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        # top container of Visualization panel
        self.frame_visualization = ttk.Frame(root_panel)
        self.frame_visualization.pack(side=tk.RIGHT, pady=10, padx=5)

        container_control = ttk.LabelFrame(master=self.frame_control, text='control panel', padding=(2, 2, 10, 10))
        container_control.pack(padx=10, pady=5)

        # create tk variable
        self.entry_var = tk.IntVar()
        self.show_box_var = tk.IntVar()
        self.rdio_var = tk.IntVar()
        self.lbl_var = tk.StringVar()

        self.count = tk.IntVar()
        self.max_count = tk.IntVar()
        self.max_count.set(max_length)
        self.lbl_var.set('{}/{}'.format(self.count.get() + 1, self.max_count.get()))

        # container for file navigation
        nav_container = ttk.LabelFrame(container_control, text='File navigation')
        nav_container.pack(side=tk.TOP, pady=10, padx=5)

        # adding elements int the navigation container
        label1 = ttk.Label(nav_container, text='Show')
        label1.grid(row=0, column=0, padx=8, pady=5, sticky='E')
        label11 = ttk.Label(nav_container, text='Image number:')
        label11.grid(row=0, column=1, padx=2, pady=5, sticky='W')

        entry = ttk.Entry(nav_container, width=5, textvariable=self.entry_var)
        entry.grid(row=0, column=2, padx=5, pady=5, sticky='E')

        self.prev_btn = ttk.Button(nav_container, text='prev', command=self.on_prev_clicked)
        self.prev_btn.grid(row=1, column=0, padx=2, pady=5, sticky='W')

        self.dynamic_label = ttk.Label(nav_container, textvariable=self.lbl_var)
        self.dynamic_label.grid(row=1, column=1, padx=2, pady=5)

        self.next_btn = ttk.Button(nav_container, text='next', command=self.on_next_clicked)
        self.next_btn.grid(row=1, column=2, padx=1, pady=5, sticky='E')

        # container for drawing 2D bbox and id for objects
        obj_detect_container = ttk.LabelFrame(container_control, text='Object detection', padding=(2, 2, 10, 10))
        obj_detect_container.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)

        self.show_box = tk.Checkbutton(obj_detect_container, text='Show 2D box', variable=self.show_box_var)
        self.show_box.pack(side=tk.TOP, anchor=tk.W, pady=5)

        id_container = ttk.LabelFrame(obj_detect_container, text='Show object label', padding=(2, 2, 10, 10))
        id_container.pack(side=tk.RIGHT, fill=tk.X, expand=tk.YES, padx=5, pady=10)

        self.id_rdio = tk.Radiobutton(id_container, text=OBJ_ID, variable=self.rdio_var, value=1)
        self.id_rdio.grid(row=0, column=0, padx=8, pady=5)
        self.typ_rdio = tk.Radiobutton(id_container, text=OBJ_TYP, variable=self.rdio_var, value=2)
        self.typ_rdio.grid(row=1, column=0, padx=8, pady=5)

        self.save_btn = ttk.Button(obj_detect_container, text='save')
        self.save_btn.pack(side=tk.LEFT, anchor='sw', padx=5, pady=10)

        # Visualization
        self.container_visualization = ttk.LabelFrame(master=self.frame_visualization, text='visualization panel')
        self.container_visualization.pack()

        # load all files and set the max size

        self.origin_img_lbl = None
        self.copy_img_lbl = None

        # VisualizationPanel.MAX_COUNT = max_count
        print('len of pic: ', self.max_count.get())
        # ControlPanel.MAX_COUNT = VisualizationPanel.MAX_COUNT

        self.json_file_container = ttk.LabelFrame(master=self.container_visualization, text='JSON-File content',
                                                  padding=(2, 2, 10, 10))
        self.json_file_container.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

        self.img_orig_container = ttk.LabelFrame(master=self.container_visualization, text='Original',
                                                 padding=(2, 2, 10, 10))
        self.img_orig_container.pack(side=tk.LEFT)

        self.img_copy_container = ttk.LabelFrame(master=self.container_visualization, text='Copy',
                                                 padding=(2, 2, 10, 10))
        self.img_copy_container.pack(side=tk.RIGHT)

        # add a scrollbar to text widget
        scrollbar = tk.Scrollbar(self.json_file_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.json_content = tk.Text(self.json_file_container, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15)
        self.json_content.pack(padx=8, pady=10)
        self.json_content.delete(1.0, tk.END)  # delete the content of text area

        scrollbar.config(command=self.json_content.yview)

        # load pictures and put them in the frame
        array_img, img_name = CustomCarlaDataset.on_load_img(self.count.get())
        re_arrange = CustomCarlaDataset.rearrang_img_for_gui(array_img)
        origin_img = Image.fromarray(re_arrange)

        # resize the image to diplay on the GUI
        origin_img.thumbnail((420, 440), Image.ANTIALIAS)
        # print(origin_img)
        img_lbl = ImageTk.PhotoImage(image=origin_img)
        self.origin_img_lbl = ttk.Label(self.img_orig_container, image=img_lbl)
        self.origin_img_lbl.pack(padx=8, pady=8)
        self.origin_img_lbl = img_lbl

        self.copy_img_lbl = ttk.Label(self.img_copy_container, image=img_lbl)
        self.copy_img_lbl.pack(padx=8, pady=8)
        self.copy_img_lbl = img_lbl
        # display picture
        self.on_show_json_content(self.count.get())
        self.m = master
        print('MASTER: ', self.m.winfo_width(), self.m.winfo_height())

    def on_next_clicked(self):
        if self.count.get() < self.max_count.get():
            # MainPanel2.COUNT += 1
            self.count.set(self.count.get() + 1)
            # pass the result to a function
            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()
            print('########## GEOMETRIE in BTN NEXT')
            print('ORG: ', self.img_orig_container.winfo_width(), ', ', self.img_orig_container.winfo_height())
            print('CPY: ', self.img_copy_container.winfo_width(), ', ', self.img_copy_container.winfo_height())
            print(self.img_orig_container.winfo_geometry())
            print('MASTER: in METH: ', self.m.winfo_width(), self.m.winfo_height())
        else:
            self.count.set(self.max_count.get())
            # self.count_var.set(count)
            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()

    def on_prev_clicked(self):
        if self.count.get() > 0:
            self.count.set(self.count.get() - 1)
            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()
        else:
            self.count.set(0)
            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()

    def _on_update_text(self):
        self.lbl_var.set('{}/{}'.format(self.count.get() + 1, self.max_count.get()))
        print('label updated: {}/{}'.format(self.count.get() + 1, self.max_count.get()))

    def on_show_img_original(self, count):
        print('on show original')
        array_img, img_name = CustomCarlaDataset.on_load_img(count)
        # print(type(array_img), ' 1')
        # print(array_img)
        re_arrange = CustomCarlaDataset.rearrang_img_for_gui(array_img)
        origin_img = Image.fromarray(re_arrange)
        print('CONTAINER: ', self.img_orig_container.winfo_height())
        # resize the image to diplay on the GUI
        origin_img.thumbnail((420, 440), Image.ANTIALIAS)
        # print(origin_img)
        img_lbl = ImageTk.PhotoImage(image=origin_img)
        print("LABL: ", img_lbl.height())

        print('reset CONTAINER HEIGHT: ', self.img_orig_container.size)

        self.origin_img_lbl = ttk.Label(self.img_orig_container, image=img_lbl)
        self.origin_img_lbl.pack(padx=8, pady=8)
        self.origin_img_lbl = img_lbl
        print('SELF LABL: ', self.origin_img_lbl.height())

    def on_show_img_copy(self, count):
        img_arr, img_name = CustomCarlaDataset.on_load_img(count)
        re_arrange = CustomCarlaDataset.rearrang_img_for_gui(img_arr)
        origin_img = Image.fromarray(re_arrange)

        # resize the image to diplay on the GUI
        origin_img.thumbnail((420, 440), Image.ANTIALIAS)
        # print(origin_img)
        img_lbl = ImageTk.PhotoImage(image=origin_img)
        self.copy_img_lbl = ttk.Label(self.img_copy_container, image=img_lbl)
        self.copy_img_lbl.pack(padx=8, pady=8)
        self.copy_img_lbl = img_lbl

    def on_show_json_content(self, count):
        print('JSON ', count)
        content = CustomCarlaDataset.on_load_file(count)
        # delete the old content and put the new one
        self.json_content.delete(1.0, tk.END)
        print('######### start of json file ########## ')
        # print('{')
        self.json_content.insert(tk.INSERT, '{\n')
        for k, v in content.items():
            if isinstance(v, dict):
                # print('\t', k, ':{')
                self.json_content.insert(tk.INSERT, '\t' + '\"' + str(k) + '\"' + ':' + '{\n')
                for nk, nv in v.items():
                    if isinstance(nv, dict):
                        # print('\t\t', nk, ':', '{')
                        self.json_content.insert(tk.INSERT, '\t\t' + '\"' + str(nk) + '\":{\n')
                        for nnk, nnv in nv.items():
                            # print('\t\t\t', nnk, ':', nnv, ',')
                            self.json_content.insert(tk.INSERT, '\t\t\t' + '\"' + str(nnk) + '\":' + str(nnv) + ',\n')
                        # print('\t\t}')
                        self.json_content.insert(tk.INSERT, '\t\t},\n')
                    elif isinstance(nv, list):
                        pass
                    else:
                        # print('\t\t', nk, ':', nv, ',')
                        self.json_content.insert(tk.INSERT, '\t\t\"' + str(nk) + '\":' + str(nv) + ',\n')
                # print('\t},')
                self.json_content.insert(tk.INSERT, '\t},\n')
            elif isinstance(v, list):
                # print('\t', k, ':[')
                self.json_content.insert(tk.INSERT, '\t\"' + str(k) + '\":[\n')
                for elem in v:
                    # print('\t\t{')
                    self.json_content.insert(tk.INSERT, '\t\t{\n')
                    if isinstance(elem, dict):
                        for nk_elem, nv_elem in elem.items():
                            if isinstance(nv_elem, dict):
                                # print('\t\t\t\t', nk_elem, ': {')
                                self.json_content.insert(tk.INSERT, '\t\t\t\"' + str(nk_elem) + '\":{\n')
                                for nnk_elem, nnv_elem in nv_elem.items():
                                    # print('\t\t\t\t\t', nnk_elem, ':', nnv_elem, ',')
                                    self.json_content.insert(tk.INSERT, '\t\t\t\t\"' + str(nnk_elem) + '\":' + str(
                                        nnv_elem) + ',\n')
                                # print('\t\t\t\t},')
                                self.json_content.insert(tk.INSERT, '\t\t\t},\n')
                            else:
                                # print('\t\t\t\t', nk_elem, ':', nv_elem, ',')
                                self.json_content.insert(tk.INSERT,
                                                         '\t\t\t\"' + str(nk_elem) + '\":' + str(nv_elem) + ',\n')
                    # print('\t\t},')
                    self.json_content.insert(tk.INSERT, '\t\t},\n')
                # print('\t]')
                self.json_content.insert(tk.INSERT, '\t]\n')
            else:
                # print('\t', k, ': ', v, ',')
                self.json_content.insert(tk.INSERT, '\t\"' + str(k) + '\":' + str(v) + ',\n')
        # print('}')
        self.json_content.insert(tk.INSERT, '\n}')
        print('######## end of json ########')


if __name__ == '__main__':
    app = MainApp()
    app.main_window.mainloop()

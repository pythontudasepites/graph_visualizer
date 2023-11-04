import tkinter as tk
from itertools import count
from graph_model import Vertex, Graph


class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # A modellből létrehozzuk a gráf példányt.
        self.graph = Graph()
        # A főablak címe és mérete.
        self.title('Gráf rajzoló')
        self.geometry('1200x600')
        # Három keretbe rendezzük a grafikus felületet. Az egyik a parancsgombokat tárolja, a másik a vásznat,
        # a harmadik pedig az eredményeket megjelenítő felületet.
        self.frame0 = tk.Frame(self, height=50)
        self.frame1, self.frame2 = tk.Frame(self, width=600, bg='silver'), tk.Frame(self, width=600, bg='silver')
        self.frame1.pack_propagate(False)
        self.frame2.pack_propagate(False)
        # A vászon és az eredménymegjelenítés grafikus elemei.
        self.cnv = tk.Canvas(self.frame1, bg='LightSkyBlue1')
        self.output_var = tk.StringVar(self)
        self.output_label = tk.Label(self.frame2, bg='white', font=('Consolas', 14, 'bold'), justify=tk.LEFT,
                                     anchor='nw', textvariable=self.output_var)
        # A különféle parancsokhoz a nyomógombok létrehozása és a megfelelő metódusok hozzárendelése.
        common_configs = dict(font=('Segoe UI', 10, 'bold'))
        self.buttons = [tk.Button(self.frame0, text='Törlés',
                                  command=self.clear, **common_configs),
                        tk.Button(self.frame0, text='Szomszédsági kapcsolatok', **common_configs,
                                  command=lambda: self.output_var.set(self.get_adjacency())),
                        tk.Button(self.frame0, text='Szélességi bejárás', **common_configs,
                                  command=lambda: self.output_var.set(self.get_bfs(self.start_vertex_entry.get()))),
                        tk.Button(self.frame0, text='Mélységi bejárás', **common_configs,
                                  command=lambda: self.output_var.set(self.get_dfs(self.start_vertex_entry.get())))]
        # A teljes gráfbejáráshoz meg lehet adni a kezdő csúcsot egy beviteli mezőben.
        self.entry_lbl = tk.Label(self.frame0, text='Kezdőcsúcs: ', **common_configs)
        self.start_vertex_entry = tk.Entry(self.frame0, width=5, font=('Consolas', 14, 'bold'))
        self.start_vertex_entry.insert(0, '0')

        self.vertex_label_gen = count()  # A csúcsok címkéinek azonosítóit kiadó generátor.
        self.r = 20  # A csúcsokat megjelenítő körök sugara.

        # Grafikus elemek lehelyezése.
        self.place_widgets()
        # Grafikus elemek, események és eseménykezelők összerendelése.
        self.bind_event_handlers()

        # Az összekötéshez kijelölt kezdő- és végcsúcs. Ha None, akkor nincs kijelölt csúcs.
        self.selected_vertex1 = self.selected_vertex2 = None

    def place_widgets(self):
        """Az egyes grafikus elemek lehelyezése a főablakban és a keretekben."""
        self.frame0.pack(side=tk.TOP, fill=tk.X, expand=False, padx=3, pady=1)
        self.frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 1), pady=1)
        self.frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 3), pady=1)

        for widget in (*self.buttons, self.entry_lbl, self.start_vertex_entry):
            widget.pack(side=tk.LEFT, fill=tk.X, expand=False, padx=2, pady=2)

        self.cnv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.output_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

    def bind_event_handlers(self):
        """Grafikus elemek, események és eseménykezelők összerendelése."""
        # Vászon felett Ctrl+bal egér -> csúcs lehelyezés
        self.cnv.bind('<Control Button 1>', self.add_vertex)
        # A csúcsok összekötéséhez a csúcsokat ki kell jelölni. Ehhez a csúcsot reprezentáló kör és címke
        # elemekhez eseményeket és a kijelölést végző eseménykezelőt rendeljük.
        # A jobb egérgomb lenyomásával kijelölt csúcsok között nem irányított élt tudunk létrehozni.
        self.cnv.tag_bind('vertex', '<Button 3>', self.select_vertices_and_connect)
        self.cnv.tag_bind('vertex_label', '<Button 3>', self.select_vertices_and_connect)
        # A Ctrl+jobb egérgomb lenyomásával kijelölt csúcsok között irányított élt tudunk létrehozni.
        self.cnv.tag_bind('vertex', '<Control Button 3>', lambda e: self.select_vertices_and_connect(e, directed=True))
        self.cnv.tag_bind('vertex_label', '<Control Button 3>',
                          lambda e: self.select_vertices_and_connect(e, directed=True))
        # Dupla bal egérgomb kattintással kijelölhető egy él.  csúcsok között irányított élt tudunk létrehozni.
        self.cnv.tag_bind('edge', '<Double Button 1>', self.select_edge)
        # Kijelölt él jobb egérgomb kattintással törölhető.
        self.cnv.tag_bind('edge', '<Button 3>', self.remove_edge)

    def clear(self):
        """Az aktuális gráf és megjelenítésének törlése, ami egy új gráf készítését teszi lehetővé."""
        self.graph = Graph()
        self.vertex_label_gen = count()
        self.cnv.delete('all')
        self.output_var.set('')

    def get_adjacency(self):
        """Az aktuális gráf szomszédsági viszonyait reprezentáló karakterláncot ad vissza."""
        txt = ''
        if self.graph.vertices:
            txt = 'Szomszédsági kapcsolatok:\n'
            txt += str(self.graph)
        return txt

    def get_bfs(self, start_label: str):
        """Az aktuális gráf adott csúcstól kezdődő teljes szélességi bejárásának sorrendjét reprezentáló
        karakterláncot ad vissza.
        """
        txt = ''
        if self.graph.vertices:
            txt = 'Szélességi bejárás:\n'
            txt += f' {chr(0x279E)} '.join(
                str(vertex.label) for vertex in self.graph.breadth_first_iterator(start_label))
        return txt

    def get_dfs(self, start_label: str):
        """Az aktuális gráf adott csúcstól kezdődő teljes mélységi bejárásának sorrendjét reprezentáló
        karakterláncot ad vissza.
        """
        txt = ''
        if self.graph.vertices:
            txt = 'Mélységi bejárás:\n'
            txt += f' {chr(0x279E)} '.join(str(vertex.label) for vertex in self.graph.depth_first_iterator(start_label))
        return txt

    def add_vertex(self, event):
        """Csúcs felvétele a gráfba az egérmutató koordinátapozíciójában."""
        x, y = event.x, event.y
        vertex_label:str = str(next(self.vertex_label_gen))  # A következő csúcscímke kikérése.
        # A csúcs egy körrel lesz ábrázolva, amelyben a csúcsazonosító címke mint szöveg látszik.
        self.cnv.create_oval(x - self.r, y - self.r, x + self.r, y + self.r, fill='white', width=3,
                             tags=('vertex', vertex_label))
        self.cnv.create_text(x, y, text=vertex_label, font=('Consolas', 16, 'bold'), tags='vertex_label')
        # Létrehozzuk a modellben is a csúcsobjektumot.
        self.graph.vertices[vertex_label] = Vertex(vertex_label)

    def get_vertex_and_label_item_ids(self, x, y):
        """Az x,y koordinátáknál található csúcs és címke elem azonosítóival tér vissza."""
        overlapping_items = self.cnv.find_overlapping(x - self.r, y - self.r, x + self.r, y + self.r)
        vertex_ovalitem_id = [item_id for item_id in overlapping_items if self.cnv.type(item_id) == 'oval'][0]
        vertex_label_textitem_id = [item_id for item_id in overlapping_items if self.cnv.type(item_id) == 'text'][0]
        return vertex_ovalitem_id, vertex_label_textitem_id

    def select_vertices_and_connect(self, event, directed=False):
        """Csúcsok kijelölése éllel való összekötéshez. Ha mindkét csúcs ki van jelölve, akkor az
        összekötés is megtörténik.
        """
        x, y = event.x, event.y
        # Az x,y helyen levő csúcs meghatározása.
        selected_vertex = self.get_vertex_and_label_item_ids(x, y)[0]

        if self.selected_vertex1 is None:
            self.selected_vertex1 = selected_vertex
        elif self.selected_vertex2 is None:
            self.selected_vertex2 = selected_vertex
            self.connect_vertices(directed)  # Miután a második csúcs is ki van választva, összekötjük őket.
            # Ha megtörtént az összekötés, akkor a két csúcs kijelölt státuszát megszüntetjük.
            self.selected_vertex1 = self.selected_vertex2 = None

    def connect_vertices(self, directed=False):
        """A két kijelölt csúcs közé egy vonalat húz.
        Ha az él irányított, akkor a nyíl a korábban kijelölttől a később kijelöltig mutat.
        """
        # Ellenőrizzük, hogy nincs-e már ilyen él.
        for edge_line_id in self.cnv.find_withtag('edge'):
            edge_line_tags = self.cnv.gettags(edge_line_id)
            v1_id, v2_id = edge_line_tags[1], edge_line_tags[2]
            if {v1_id, v2_id} == {str(self.selected_vertex1), str(self.selected_vertex2)}:
                return
        # Csúcsot önmagával nem kötünk össze.
        if self.selected_vertex1 == self.selected_vertex2:
            return

        # Az eltérő, összekötendő csúcskörök befoglaló koordinátái, és középpont koordinátái.
        v1_coords, v2_coords = self.cnv.coords(self.selected_vertex1), self.cnv.coords(self.selected_vertex2)
        v1x0, v1y0 = (v1_coords[0] + v1_coords[2]) / 2, (v1_coords[1] + v1_coords[3]) / 2
        v2x0, v2y0 = (v2_coords[0] + v2_coords[2]) / 2, (v2_coords[1] + v2_coords[3]) / 2
        # A csúcsok középpontjait összekötő vonal rajzolása, és felcímkézve a kezdő- és végcsúcs körök azonosítójával.
        edge_line_id = self.cnv.create_line(v1x0, v1y0, v2x0, v2y0, width=3,
                                            tags=('edge', str(self.selected_vertex1), str(self.selected_vertex2)))
        if directed:
            self.cnv.itemconfig(edge_line_id, arrow=tk.LAST, arrowshape=(10, 12, 5))
            length = pow((v2x0 - v1x0) ** 2 + (v2y0 - v1y0) ** 2, 0.5)
            reduced_length = length - self.r - 15
            scale_factor = reduced_length / length
            self.cnv.scale(edge_line_id, (v1x0 + v2x0) / 2, (v1y0 + v2y0) / 2, scale_factor, scale_factor)

        # Az összekötővonalat a megjelenítési lista legaljára helyezzük, hogy ne takarja el a csúcskört és címkét.
        self.cnv.tag_lower(edge_line_id)
        # Kikeressük az összekötendő csúcsok címkéit, hogy a modellben is össze tudjuk kötni egy éllel.
        v1_lbl, v2_lbl = self.cnv.gettags(self.selected_vertex1)[1], self.cnv.gettags(self.selected_vertex2)[1]
        # Csúcsok összekötése a gráf modellben. Ha nem irányított az él, akkor mindkét irányban.
        self.graph.add_connection(v1_lbl, v2_lbl)
        if not directed:
            self.graph.add_connection(v2_lbl, v1_lbl)

    def select_edge(self, event):
        """Az egérmutatóhoz legközelebb eső élt kijelöltnek címkéz, és megváltoztatja a színét.
        Ha egy már kijelölt él a legközelebbi él, akkor a kijelölést érvényteleníti.
        """
        x, y = event.x, event.y
        # Megnézzük, hogy van-e már kijelölt él. Ha van, akkor azt nem kijelöltté tesszük.
        if old_edges := self.cnv.find_withtag('selected_edge'):
            self.cnv.dtag(old_edges[0], 'selected_edge')
            self.cnv.itemconfig(old_edges[0], fill='black')

        # Az egérmutatónál levő élt kijelöltnek nyilvánítjuk egy taggel, és
        # megváltoztatjuk a vonal alapszínét.
        new_edges = self.cnv.find_closest(x, y)
        if new_edges != old_edges:
            self.cnv.addtag_closest('selected_edge', x, y)
            self.cnv.itemconfig(new_edges[0], fill='red')

    def remove_edge(self, event):
        x, y = event.x, event.y
        if self.cnv.find_withtag('selected_edge'):
            edge_to_remove = self.cnv.find_withtag('selected_edge')[0]
            # A kijelölt él eltávolítása a vászonról.
            x1, y1, x2, y2 = self.cnv.coords(edge_to_remove)
            v1_id, v1_lbl_id = self.get_vertex_and_label_item_ids(x1, y1)
            v2_id, v2_lbl_id = self.get_vertex_and_label_item_ids(x2, y2)
            self.cnv.delete(edge_to_remove)
            # A kijelölt él eltávolítása a modellből.
            v1_lbl, v2_lbl = self.cnv.itemcget(v1_lbl_id, 'text'), self.cnv.itemcget(v2_lbl_id, 'text')
            self.graph.remove_edge(v1_lbl, v2_lbl)

    def run(self):
        self.mainloop()

# Alkalmazás indítás
graph_app = GraphApp()
graph_app.run()

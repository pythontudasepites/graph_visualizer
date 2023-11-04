from collections import defaultdict


class Vertex:
    def __init__(self, label, data=None):
        self.label = label
        self.data = data

    def __repr__(self):
        args = f'{self.label}, {self.data}' \
            if self.data is not None else f'{self.label}'
        return f'{type(self).__name__}({args})'


class Graph:
    def __init__(self):
        self.vertices: dict[str, Vertex] = dict()
        self.neighbors: dict[str, set[tuple[str, int | float]]] = defaultdict(set)

    def __str__(self):
        w = max(len(vname) for vname in self.neighbors)
        graph_string = []
        for vertex_label, neighbors in self.neighbors.items():
            nbrs = str(neighbors).strip("{}") if neighbors else ''
            graph_string.append(f'{vertex_label:{w}} {chr(0x279E)} {nbrs}\n')

        return ''.join(graph_string)

    def add_connection(self, start_vertex_label: str, end_vertex_label: str, weight=1):
        """A megadott kezdő- és végcsúcs közötti élt határozza meg a gráfban.
        Opcionálisan az élhez rendelhető egy súly is.
        Ha a csúcsok nem léteznek még, akkor azokat létrehozza.
        """
        # Hozzáadjuk az adott induló csúcshoz tartozó halmazhoz a végcsúcs és az él súlyából képzett párost.
        # Ha az adott csúcs még nincs a szótárban, akkor felveszi, és rögtön hozzárendel egy halmaz konténert.
        self.neighbors[start_vertex_label].add((end_vertex_label, weight))
        # Felvesszük a szomszédságot leíró szótárba a végcsúcsot, ha az nem létezik még, és amihez
        # rögtön hozzárendelünk egy halmaz konténert.
        self.neighbors[end_vertex_label]
        # A tényleges csúcs objektumokat is létrehozzuk és eltároljuk, ha még nem léteznek.
        if start_vertex_label not in self.vertices:
            self.vertices.update({start_vertex_label: Vertex(start_vertex_label)})
        if end_vertex_label not in self.vertices:
            self.vertices.update({end_vertex_label: Vertex(end_vertex_label)})

    def remove_edge(self, start_vertex_label: str, end_vertex_label: str):
        """A megadott kezdő- és végcsúcs közötti élt eltávolítja."""
        self.neighbors[start_vertex_label] = set(item for item in self.neighbors[start_vertex_label]
                                                 if item[0] != end_vertex_label)

        self.neighbors[end_vertex_label] = set(item for item in self.neighbors[end_vertex_label]
                                               if item[0] != start_vertex_label)

    def remove_vertex(self, vertex_label: str):
        """A megadott csúcsot eltávolítja a gráfból."""
        # A csúcs objektumok közül eltávolítjuk a csúcsot.
        self.vertices.pop(vertex_label)
        # A szomszédságot leíró szótárból eltávolítjuk a megadott csúcsot.
        self.neighbors.pop(vertex_label)
        # Minden olyan csúcs esetén, amelynek szomszédja volt, kivesszük a szomszéd csúcsok közül.
        for vxl, nbs in self.neighbors.items():
            self.neighbors[vxl] = set(item for item in nbs if item[0] != vertex_label)

    def set_vertex_data(self, vertex_label, vertex_data):
        """Egy adott csúcshoz értéket rendel."""
        if vx := self.vertices.get(vertex_label):
            vx.data = vertex_data

    @staticmethod
    def check_edge_weight_values(fn):
        def inner(self, start_vertex_label: str):
            # Ellenőrizni kell, hogy minden élsúly szám-e, és nem negatív.
            try:
                for vertex_label, neightbor_set in self.neighbors.items():
                    for neighbor_label, edge_distance_to_neighbor in neightbor_set:
                        # Ha a konverzió nem lehetséges, akkor az azt jelenti, hogy a súly nem szám, vagy
                        # számnak nem tekinthető karaktersorozat a súly. Ekkor típushibát jelző kivétel dobódik.
                        weight_num = float(edge_distance_to_neighbor)
                        # Ha ugyan a súly szám, de negatív, akkor ezt jelző kivétel keletkezik.
                        if weight_num < 0:
                            raise ValueError('Minden élsúly nem negatív valós szám kell, hogy legyen')
            except (TypeError, ValueError):
                raise TypeError(
                    f'{vertex_label}-{neighbor_label} csúcsok közötti él súlya:{edge_distance_to_neighbor}. '
                    f'Minden él súlyának valós számnak kell lenni.')

            return fn(self, start_vertex_label)

        return inner

    @check_edge_weight_values
    def shortest_paths(self, start_vertex_label: str):
        """Visszaadja egy szótárban a megadott csúcstól számított legrövidebb út hosszát, valamint az
        összes csúcshoz vezető legrövidebb útvonalat.
        """
        # Minden kiinduló ponttól számított, eddig ismert legrövidebb úthosszat minden csúcsra végtelenre
        # állítjuk, hiszen ezeket kezdetben nem ismerjük még.
        for vertex_label in self.vertices:
            self.set_vertex_data(vertex_label, [float('inf'), None])
        # A kiinduló csúcs eddig ismert legrövidebb úthosszát 0-ra állítjuk, hiszen önmagától nulla távra van.
        self.set_vertex_data(start_vertex_label, [0, None])

        # Minden csúcsot még nem vizsgáltnak (nem látogatottnak) állítjuk be.
        unvisited: dict = {label: vertex for label, vertex in self.vertices.items()}

        while unvisited:
            # Egy olyan új aktuális vizsgálni kivánt csúcsot választunk a még nem látogatott csúcsok közül, amely
            # ezek közül a legrövidebb útvonallal rendelkezik.
            current = min(unvisited, key=lambda lbl: unvisited[lbl].data[0])

            # Az aktuális csúcsra kiszámítjuk a távolságot az összes nem látogatott szomszédjától.
            for neighbor, edge_distance_to_neighbor in self.neighbors[current]:
                if neighbor in unvisited:
                    neighbor_vertex_obj = self.vertices[neighbor]
                    # Ha a szomszéd csúcs eddig ismert legrövidebb úthossza nagyobb, mint a jelenlegi csúcs
                    # eddig ismert legrövidebb úthossza + a közöttük levő út hossza, akkor a szomszéd csúcs eddig
                    # ismert legrövidebb úthosszát erre az összegre módosítjuk.
                    if (distance := self.vertices[current].data[0] + float(edge_distance_to_neighbor)) < \
                            neighbor_vertex_obj.data[0]:
                        neighbor_vertex_obj.data = [distance, current]
            # Miután az aktuális csúcs minden szomszédját megvizsgáltuk és aktulizáltuk a szomszéd legrövidebb
            # távolság adatát és az odavezető megelőző csúcsot, az aktuális csúcsot megvizsgáltnak tekintjük és
            # kivesszük a még meg nem látogatottak listájából.
            unvisited.pop(current)

        # Segédfüggvény
        def shortest_path(end_vertex_label: str):
            """A start_vertex-től az argumentumként megadott végcsúcshoz vezető legrövidebb úton levő csúcsok
            listáját adja vissza a csúcsok adatai alapján.
            """
            path = []
            path.append(end_vertex_label)
            while previous_vertex := self.vertices[end_vertex_label].data[1]:
                path.append(previous_vertex)
                end_vertex_label = previous_vertex
            return path[-1::-1]

        # A visszatérési értékként szolgáló szótár előállítása, amelynek kulcsai a célcsúcsok címkéi, az
        # ezekhez tartozó értékek olyan tuple konténerek, amelyek első eleme a célcsúcsig vezető legrövidebb
        # út hossza, második eleme pedig a legrövidebb útat jelentő csúcsok listája.
        shortest_distances_and_paths = {vx_label: (self.vertices[vx_label].data[0], shortest_path(vx_label))
                                        for vx_label in self.vertices
                                        if self.vertices[vx_label].data[0] != float('inf')}

        return shortest_distances_and_paths

    def breadth_first_traversal(self, start_vertex_label: str) -> list[str]:
        visited = []  # A már bejárt (megvizsgált, feldolgozott) csúcsok listája.
        # A vizsgálatra váró csúcsok listája, ami kezdetben csak a kiinduló csúcsot tartalmazza.
        unvisited = [start_vertex_label]
        while unvisited:
            # A vizsgálatra váró csúcsok listájából vesszük a soron következőt.
            current = unvisited.pop(0)
            if current not in visited:
                # Ha az aktuálisan vizsgált csúcs nincs a meglátogatottak között, akkor felvesszük ezek listájába.
                visited.append(current)
                # Összegyűjtjük az aktuálisan vizsgált csúcs szomszédait.
                neighbours = [neighbour for neighbour, weight in self.neighbors[current]]
                # Kiválogatjuk a szomszédok közül a még nem vizsgáltakat.
                unvisited_neighbours = [neighbour for neighbour in neighbours if neighbour not in visited]
                # Ezeket hozzáadjuk a vizsgálatra váró csúcsok listájához.
                unvisited.extend(unvisited_neighbours)
        return visited

    def breadth_first_iterator(self, start_vertex_label: str) -> 'Generátor-iterátor[Vertex]':
        visited = set()  # A már bejárt (megvizsgált, feldolgozott) csúcsok halmaza.
        # A vizsgálatra váró csúcsok listája, ami kezdetben csak a kiinduló csúcsot tartalmazza.
        unvisited = [start_vertex_label]
        for vx in self.vertices.values():
            vx.data = 0
        while unvisited:
            current = unvisited.pop(0)
            if current not in visited:
                # Ha az aktuálisan vizsgált csúcs nincs a meglátogatottak között, akkor felvesszük ezek halmazába.
                visited.add(current)
                # Kiadjuk a csúcsobjektumot.
                yield self.vertices.get(current)
                neighbours = [neighbour for neighbour, weight in self.neighbors[current]]
                unvisited_neighbours = [neighbour for neighbour in neighbours if neighbour not in visited]
                unvisited.extend(unvisited_neighbours)

                for nb in unvisited_neighbours:
                    self.vertices.get(nb).data = self.vertices.get(current).data + 1

    def depth_first_iterator(self, start_vertex_label: str) -> 'Generátor-iterátor[Vertex]':
        visited = set()  # A már bejárt (megvizsgált, feldolgozott) csúcsok halmaza.
        # A vizsgálatra váró csúcsok listája, ami kezdetben csak a kiinduló csúcsot tartalmazza.
        unvisited = [start_vertex_label]  # LIFO módban fogjuk használni (verem megvalósítása).

        while unvisited:
            current = unvisited.pop()  # A LIFO konténer legutoljára betett elemét vesszük ki vizsgálatra.
            if current not in visited:
                # Ha az aktuálisan vizsgált csúcs nincs a meglátogatottak között, akkor felvesszük ezek halmazába.
                visited.add(current)
                # Kiadjuk a csúcsobjektumot.
                yield self.vertices.get(current)

                neighbours = [neighbour for neighbour, weight in self.neighbors[current]]
                unvisited_neighbours = [neighbour for neighbour in neighbours if neighbour not in visited]
                unvisited.extend(unvisited_neighbours)

    def __call__(self, start_vertex_label: str, algo='breadth_first') -> 'Generátor-iterátor[Vertex]':
        algo_iterators = dict(breadth_first=self.breadth_first_iterator,
                              depth_first=self.depth_first_iterator)
        return algo_iterators.get(algo)(start_vertex_label)



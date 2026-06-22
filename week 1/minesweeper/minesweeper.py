import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        #per essere sicuri che le celle siano mine, bisogna verificare che il numero di celle sia uguale al numero di mine.
        if len(self.cells) == self.count and self.count != 0:
            return set(self.cells)
        return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #per essere sicuri che non siano mine il numero di mine presenti tra quelle celle deve essere nullo
        if self.count == 0 and len(self.cells) > 0:
            return set(self.cells)
        return set()


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

        

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

        


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        #1) segna la cella come esplorata(aggiungi alle mosse fatte)
        self.moves_made.add(cell)
        #2) segna la cella come sicura
        self.mark_safe(cell)
        #3) aggiunge una nuova sentence basandosi sui vicini della cella stessa
        # esploriamo i vicini esclidendo la stessa
        neighbors = set()
        undeterminated_cells = set()
        mines_count = count

        for i in range (cell[0]-1,cell[0]+2):
            for j in range (cell[1]-1, cell[1]+2): 
                if (i,j) == cell:
                    continue
                neighbors.add((i,j))

                #check sui limiti del tabellone( no possiamo controllare celle che non appartengono ad esso)
                if i not in range(0,self.height) or j not in range(0,self.width):
                    neighbors.remove((i,j))

        #ora controlliamo le caselle e formuliamo le nuove frasi da aggiungere alla KB
        for neighbor in neighbors:
            if neighbor in self.mines:
                mines_count -= 1

            #se non sappiamo cos'è la mettiamo nella lista undeterminated
            elif neighbor not in self.safes and neighbor not in self.moves_made:
                undeterminated_cells.add(neighbor)

        #ho analizzato i vicino ora devo generare la frase 
        new_sentence = Sentence(undeterminated_cells, mines_count)
        self.knowledge.append(new_sentence) 


        #4)in base alla KB marcare, se possibile , le celle vicine come mine o sicure
        # devo aggiornare le info finche si fanno nuove scoperte-->ciclo while
        Knowledge_changed = True
        while Knowledge_changed:
            Knowledge_changed = False

            #creiamo i set dove inserire le celle safe e mines
            safes_to_mark = set()
            mines_to_mark = set()

            #riempiemole se possibile, estraendo le info da self.knowledge
            for sentence in self.knowledge:
                safes_to_mark = safes_to_mark.union(sentence.known_safes())
                mines_to_mark = mines_to_mark.union(sentence.known_mines())

            if safes_to_mark:   #invece del len(safes_to_mark) > 0
                Knowledge_changed = True
                for safe in safes_to_mark:
                    self.mark_safe(safe)
                    

            if mines_to_mark:
                 Knowledge_changed = True
                 for mine in mines_to_mark:
                     self.mark_mine(mine)

            #rimuoviamo le frasi vuote(di significato) aggiornando il self.knowledge
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]  #list comprehension
            
        #5) analaizzando le info presenti nella KB veddiamo se riusciamo a generare (inference) delle nuove sentences
        # per farlo dobbiamo confrontare le info intermini di sottoinsiemi per estrarne delle nuove. Ovviamente se i due insiemi sono identici
        # (le info sono uguali) non possiamo trarre nuove deduzioni
        new_sentences = []

        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 == sentence2:
                    continue #no new info

                #ora ragioniamo in termini sdi sottoinsiemi
                if sentence1.cells.issubset(sentence2.cells):
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count

                    #inferred_sentence = Sentence(new_cells, new_count)
                    if len(new_cells) > 0:
                            inferred_sentence = Sentence(new_cells, new_count)

                    #creata la nuova sentence(info) la aggiungiamo alla KN
                    if inferred_sentence not in self.knowledge and inferred_sentence not in new_sentences:
                                new_sentences.append(inferred_sentence)
        if new_sentences:
                self.knowledge.extend(new_sentences)
                knowledge_changed = True                
    
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
       #verifichiamo quindi quali sono le celle per le quali siamo sicuri che non ci siano bombe
       #che non sono state gia "esplorate" e quindi non sono presenti in moves_made
        for cell in self.safes:
                if cell not in self.moves_made:
                    return cell
        # giustamente se non ci sono celle che corrispondono ai requisiti richiesti non ci sono celle certamente sicure        
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        moves_available = []

        #generiamo un set con tutte le possibili mosse
        for i in range(self.height):
             for j in range(self.width):
                 cell = (i, j)

                 #applichiamo ora i filtri necessari
                 #1) la cella non devessere gia stata espolrata
                 #2) la cella non deve essere una mina
                 if cell not in self.moves_made and cell not in self.mines:
                     moves_available.append(cell)

        #inizializziamo l'estrazione randomica: viene effettuata finche non finiscono le caselle disponibili
        if len(moves_available) > 0:
            return random.choice(moves_available)
        return None
                       

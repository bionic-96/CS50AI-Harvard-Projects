import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #iniziamo ad iterare su ogni parola del dizionario ( dominio di ogni variabile)
        #cosi da rimuover le parole che non matchano la lunghezza
        for var in self.domains: #var è la chiave del dict ovvero ogni var è una variabile del crossword
            #ovvero un insime di caselle vuote da riempire con una parola

            #iteriamo su ogni parola del dominio della variabile var
            # crea una copia del set di parole per non incorrere in errori
            for word in self.domains[var].copy(): # self.domanins[var] etsrae il valore associato alla chiave nel dict
                
                #imponiamo Unary constraint
                if len(word) != var.length:
                    self.domains[var].remove(word) #rimuoviamo la parola dal dominio della variabile var  


    # ora implementiamo le funzioni per l'arc consistency e il backtracking search

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        #intersezione tra le variabili x y
        overlap  = self.crossword.overlaps[x, y]
        if overlap is None:
            return False #no constraint to respect
        else:
            i, j = overlap 
            
            #ora prensiamo tutte le parole di x e vediamo se per ognuna è possibile avere una parola di y
            # che matcha. quelle per cui non esiste una parola di y che matcha, le rimuoviamo dal dominio di x
            for word_x in self.domains[x].copy():
                match_found  = False

                #iteriamo per y per trovare parola che matcha, se la trovo break
                for word_y in self.domains[y]:

                    if word_x[i] == word_y[j]:
                        match_found = True
                        break
                        
                if not match_found:
                    self.domains[x].remove(word_x)
                    revised = True #aggiornato il dominio

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        #inizializziamo la coda con tutte le tuple degli archi possibili
        # per farlo dobbiamo prendere le variabili e vederne i vicini 
        if arcs is None:
            #inizializzazione coda,LIST
            queue = []           
            #prendiamo tutte le variabili e per ognuna cerchiamo i vicini di appendere alla queue
            for var in self.domains: 
                #prendo tutti i vicini e creo la tupla(arco) da inserire nella queue
                for neighbor in self.crossword.neighbors(var):
                    queue.append((var, neighbor))

        else:
            queue = list(arcs) #in caso non fosse vuota usiamo quella che viene fornita

        #processiamo la coda finche non si svuota:
        while queue:
            #estrauamo il primo arco, ( questa fa aggiornare ad ogni step il primo elemento della lista vero?)
            x, y = queue.pop(0)

            # per ogni tupla usiamo la funzione revise(x,y)
            # se la revise è True
            if self.revise(x, y):
                # se il dominio cambia, gestire la propagazione verso i vicini
                # sappiamo che è stato aggiornato il dominio, dobbiamo effettuare il controllo
                if len(self.domains[x]) == 0:
                    return False #significa che non è piu possibile continuare e il problema non è risolvibile
                
                #controllo a cascata sui vicini, tranne y
                for z in self.crossword.neighbors(x)-{y}: #{} perche è un dizionario?
                    queue.append((z, x))

        #Se la coda si svuota senza fallimenti, abbiamo raggiunto la stabilità
        return True
                

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        #andiamo ad analizzare tutte le variabili(caselle  da riempire) e 
        #andiamo a verificare che quelle in assignement, ovvero quelle a cui l'algoritmo ha gia assegnato una parola,
        # siano tutte le variabili del crossword, ALTRIMENTI L'ASSIGNMENT NON è COMPLETATO E BISOGNA CONTINUARE
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        
             #check aggiuntivo, se la variabile è presente nel dizionario ma il suo valore assegnato è nullo,
             #avvore nessuna parola è stata assegnata alla variabile
            if assignment[var] is None:
                return False     

        #Se il ciclo finisce senza mai restituire False, significa che ogni 
        #variabile ha una sua parola assegnata. Il cruciverba è pieno!
        return True   
            

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        #dopo aver verificato che il cruciverba sia stato "riempito" , verifichiamo che 
        #le parole siano consistenti tra loro, ovvero che non ci siano conflitti tra le lettere delle parole assegnate alle variabili
        #quindi che rispettino tutti i CONSTRAINTS (1. unicitò; 2.lunghezza; 3. incroci)
        
        # 1 UNICITA
        assigned_words = list(assignment.values()) #lista che abbiamo di tutte le parole assegnate
        assigned_set = set(assignment.values())    # set ( eliminazione dei duplicati)
        if len(assigned_words) != len(assigned_set):
            return False
        
        #2 VINCOLI UNARI
        for var in assignment:
               word = assignment[var]

               if len(word) != var.length:
                   return False
               
               #3 VINCOLI BINARI
               #continuo all'interno dello stesso ciclo su tutte le parole assegnate
               #prendiamo i vicini della variabile e facciamo il check
               for neighbor in self.crossword.neighbors(var):
                   
                   if neighbor in assignment:
                       
                        overlap = self.crossword.overlaps[var, neighbor]
                        
                        if overlap is not None:
                            i, j = overlap
                            #check
                            if word[i] != assignment[neighbor][j]:
                                return False
                        
        return True
    
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        def count_conflicts(word):
            """Calcola quanti valori questa 'word' esclude dai domini dei vicini."""
            conflicts = 0
            #isoliamo i vicini che non hanno ancora una parola assegnata
            unassigned_neighbors = self.crossword.neighbors(var) - set(assignment.keys())
            
            for neighbor in unassigned_neighbors:
                i, j = self.crossword.overlaps[var, neighbor]
                
                # Per ogni parola nel dominio del vicino, controlliamo se c'è conflitto
                for neighbor_word in self.domains[neighbor]:
                    if word[i] != neighbor_word[j]:
                        conflicts += 1
                        
            return conflicts

        # Trasformiamo il set del dominio in lista e lo ordiniamo usando 
        # la nostra funzione custom come criterio (ordine crescente di default)
        return sorted(list(self.domains[var]), key=count_conflicts)


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        #obbiettivo è assegnare le variabili a cui è rimasto il minor numero di parole nel dominio.
        # filtriamo le variabili non ancora ssegnate
        unassigned = [v for v in self.crossword.variables if v not in assignment] #comprehension list

        #ora ordiniamo queste variabili per numero crescente di parole possibili da assegnargli(presenti nel dominio della variabile)
        # in caso di parità usiamo il grado della variabile, ovvero il numero di vicini che ha, e prendiamo quella con il grado maggiore.

        best_var = None
        #MVR
        for current_var in unassigned:
            if best_var is None:
                best_var = current_var
                continue

            #ora vediamo se la current var è migliore dello sfidante, se no
            # #aggiorniaamo la current
            best_domain_mvr = len(self.domains[best_var])
            current_domain_mvr = len(self.domains[current_var])

            if best_domain_mvr > current_domain_mvr:
                #se lo sfidante ha meno parole nel dominio, diventa lui il current
                best_var = current_var 
            
            elif best_domain_mvr == current_domain_mvr:
                #se hanno lo stesso numero di parole nel dominio, usiamo il grado della variabile
                best_degree = len(self.crossword.neighbors(best_var))
                current_degree = len(self.crossword.neighbors(current_var))

                if best_degree < current_degree:
                    #se lo sfidante ha piu vicini, diventa lui il current
                    best_var = current_var
        return best_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        #partiamo dal caso base e vediamo se abbiamo riempito o meno il crossword(condizione di uscita)
        if self.assignment_complete(assignment):
            return assignment
        
        #scegliamo la variabile non ancora assegnata da riempire, usando la funzione select_unassigned_variable
        var = self.select_unassigned_variable(assignment)

        #dopo aver scelto la variabile, andiamo ad iterare sui valori(parole) da assegnare, 
        #usando la funzione order_domain_values per avere le parole ordinate in base al numero di conflitti che generano
        for value in self.order_domain_values(var, assignment):
            #assegniamo la parola alla variabile
            assignment[var] = value

            #verifichiamo se l'assegnamento è consistente, usando la funzione consistent
            if self.consistent(assignment):  
                #se è vera genera un true che rende vero l'if e quindi fa partire la ricorsione
                
                #se è consistente, facciamo la ricorsione per riempire le altre variabili
                result = self.backtrack(assignment) #richiama se stessa per riempire le altre variabili, se non è consistente ritorna None e quindi si passa alla prossima parola del dominio della variabile var
                if result is not None:
                    return result
            
            #se non è consistente o se la ricorsione non ha portato a una soluzione, rimuoviamo l'assegnamento e proviamo con un'altra parola
            del assignment[var]
        
        return None  #se non ci sono parole valide per la variabile, ritorniamo None
        

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

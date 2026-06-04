"""
Tic Tac Toe Player
"""

import math
import copy 
X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    #per decidere chi inizia parto con il conteggio di X e O (inizia X e si devono alternare)
    x_count = 0
    o_count = 0
    
    #inizio a contare scorrendo le righe
    for row in board:
        #continuo scorrendo ogni cella della riga
        for cell in row :
            if cell == X:
                x_count = x_count + 1
            elif cell == O:
                o_count += 1

    # ora impostiamo il calcolo per vedere chi è il giocatore
    if x_count > o_count:
        return O
    #ovviamente se sono pari tocca a X
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    #creazione set vuoto per memorizzare le mosse
    possible_action = set()
    # gli indici i e j rappr risp righe e colonne da 0 a 2
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possible_action.add((i,j)) #cosi facendo aggiungiamo la tupla(i,j) alla lista

    return possible_action



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # 1. check di validità della tupla Action (i,j). essendo una tupla (i, j), Le separiamo per comodità
    i = action[0]
    j = action[1]
    #se la cella della board è vuota la tupla della mossa corrispondente è valida altrimenti no (sarebbe gia occupata)
    if board[i][j] != EMPTY:
        raise Exception("Mossa non valida: la casella è già occupata.")
    
    #2. scopriamo a chi tocca (Player)
    current_player = player(board)

    #3. facciamo la copia della board
    new_board = copy.deepcopy(board)

    #4 applichiamo la mossa alla copia
    new_board[i][j] = current_player # stiamo assegnando X/O a seconda del player all'elemento (i,j)

    #5.restituire la copia 
    return new_board

    
   #arrivato qui


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #check sulle righe: iniziamo con ciclo for in modo da farlo per tutte e tre
    for i in range(3):
        if board[i][0] == board[i][1]== board[i][2] and board[i][0]!= EMPTY:
                return board[i][0]  #if board[i][0] is X: non è necessario poiche restituisce direttamente l'elemento

    # check sulle colonne 
    for j in range(3):
        if board[0][j] == board[1][j]== board[2][j] and board[0][j]!= EMPTY:
                return board[0][j]
        
    #check diagonali: prima principale poi l'altra
    if board[0][0] == board[1][1]== board[2][2] and board[0][0]!= EMPTY:
                return board[0][0]
    if board[0][2] == board[1][1]== board[2][0] and board[0][2]!= EMPTY:
                return board[0][2]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    game_winner = winner(board)
    # if there is a winner
    if game_winner is not None: 
         return True
    # if ther isn't a winner and the board is Full 
    if not any(EMPTY in row for row in board):
      return True
         #ALTERNATIVE WAY
         # Fonde le 3 righe in un'unica lista da 9 caselle
         #scacchiera_piatta = sum(board, []) 
         #if EMPTY not in scacchiera_piatta:
         # La scacchiera è piena!
    # otherwise, if ther isn't a winner and the board is not full 
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # non necessario: if game_state is not False: #se la partita è finita, ora devo individuare se qualcuno ha vinto o meno per restituire l'utility
    game_winner = winner(board)
    if game_winner == X:
        return 1
    elif game_winner == O:
        return -1
    else:
        return 0
         
         
#before minimax create the 2 support functions max_value and min_value

def max_value(board):
     """ evaluate the maximum value for X"""
     # se il gioco è terminato restituisci direttamente l'utility value
     if terminal(board) is True:
          return utility(board)
     #dovendo massimizzare partiamo dal valore piu basso possibile
     v = -math.inf

     #ora esploriamo le possibili mosse (partendo dalla board Generica)
     for possible_action in actions(board):
          #Calcoliamo il massimo tra il valore attuale e la risposta di O
          v = max(v,min_value(result(board,possible_action)))
        
     return v

def min_value(board):
     """ evaluate the minimum value for O"""
     # se il gioco è terminato restituisci direttamente l'utility value
     if terminal(board) is True:
          return utility(board)
     #dovendo minimizzare partiamo dal valore piu alto possibile
     v = math.inf

     #ora esploriamo le possibili mosse (partendo dalla board Generica)
     for possible_action in actions(board):
          #Calcoliamo il minimo tra il valore attuale e la risposta di X
          v = min(v,max_value(result(board, possible_action)))
        
     return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    ###RIFARLO DA SOLO SENZA SPOILER###

    # Se il gioco è già finito, non ci sono mosse da fare
    if terminal(board):
        return None

    # Scopriamo a chi tocca
    current_player = player(board)

    # SE TOCCA A X (Vuole massimizzare)
    if current_player == X:
        best_score = -math.inf
        best_action = None
        
        for action in actions(board):
            # Simula la mossa e chiede a min_value quale sarà il punteggio finale
            score = min_value(result(board, action))
            
            # Se questo punteggio è migliore di quello registrato finora, lo salviamo
            if score > best_score:
                best_score = score
                best_action = action
                
        return best_action

    # SE TOCCA A O (Vuole minimizzare)
    else:
        best_score = math.inf
        best_action = None
        
        for action in actions(board):
            # Simula la mossa e chiede a max_value quale sarà il punteggio finale
            score = max_value(result(board, action))
            
            # Se questo punteggio è "minore" (migliore per O), lo salviamo
            if score < best_score:
                best_score = score
                best_action = action
                
        return best_action
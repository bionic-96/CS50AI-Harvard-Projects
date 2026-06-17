from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    #imposto e regole del personaggio,
    Or(AKnight, AKnave), #deve essere per forza uno dei due
    Not(And(AKnight, AKnave)), #non può essere entrambi
    
    #la dichiarazione di A
    Biconditional(AKnight, And(AKnight,AKnave)) # stiamo dicendo che A è un cavaliere
                                                #se e solo se la sua affermazione è vera
     )                                          # tramite le regole scritte sopra l'AI riconosce che è falsa )


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    #imposto e regole dei personaggi: (same as above)
    #A
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    #B
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    #la dichiarazione di A
    Biconditional(AKnave, Not(And(AKnave, BKnave)))
    
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    #imposto e regole dei personaggi: (same as above)
    #A
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    #B
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    #la dichiarazione di A
    Biconditional(AKnight , Or( And( AKnight,BKnight), And(AKnave,BKnave) ) ),

    #la dichiarazione di B
    Biconditional(BKnight , Or( And( AKnight,BKnave), And(AKnave,BKnight) ) )


)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    #A
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),
    #B
    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),
    #C
    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),

    #la dichiarazione di A
    Or( 
        Biconditional(AKnight, AKnight), #A dice AKnight  
        Biconditional(AKnight,AKnave), #A dice AKnave      
    ),

    #la prima dichiarazione di B
    Biconditional(BKnight,Biconditional(AKnight, AKnave)), 

    #la seconda dichiarazione di B
    Biconditional(BKnight, CKnave),

    #la dichiarazione di C
    Biconditional(CKnight, AKnight) #C dice che AKnight e quinde se Aknite vero è vero Cknigh o viceversa

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()

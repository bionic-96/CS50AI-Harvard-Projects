import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_prob = 1
    #andiamo a valutare per ogni persona la probabilità di avere il gene e il tratto
    for person in people:
        # determiniamo il numero di geni della persona
        if person in one_gene:
            genes = 1
        elif person in two_genes:
            genes = 2
        else:
            genes = 0
        
        #ora ansiamo a vedere se la persona manifesta il tratto
        
        has_trait = person in have_trait

        #calcoliamo ora la probabilità dei geni per una persona generica
        #partiamo dal caso in cui la persona non abbia genitori
        if people[person]["mother"] is None and people[person]["father"] is None:
            #se non ci sono i genitori probabilità incondiz
            gene_prob = PROBS["gene"][genes]
        else:
            #se ha i genitori dobbiamo impostare il problema usando la probabilita condicionata  
            mother = people[person]["mother"]
            father = people[person]["father"]

            # Funzione di supporto per calcolare la probabilità che un genitore passi il gene
            def pass_prob(parent_name):
                if parent_name in one_gene:
                    # Se ha 1 gene, 50% di passarlo (mutazione annullata matematicamente)
                    return 0.5
                elif parent_name in two_genes:
                    # Se ha 2 geni, lo passa a meno che non muti
                    return 1 - PROBS["mutation"]
                else:
                    # Se ha 0 geni, lo passa solo se muta
                    return PROBS["mutation"]

            p_from_mother = pass_prob(mother) #PROBABILITà che venga trasmesso il gene dalla mamma
            p_from_father = pass_prob(father) #probabilità che venga trasmesso il gene dal papà

            # Combina le probabilità dei genitori in base ai geni del figlio
            if genes == 2:
                # Deve riceverlo da ENTRAMBI
                gene_prob = p_from_mother * p_from_father
            elif genes == 1:
                # Da madre E non da padre, OPPURE da padre E non da madre
                gene_prob = (p_from_mother * (1 - p_from_father)) + (p_from_father * (1 - p_from_mother))
            else: # genes == 0
                # Non deve riceverlo da NESSUNO dei due
                gene_prob = (1 - p_from_mother) * (1 - p_from_father)

        # 4. Calcola la probabilità del tratto (condizionata ai geni)
        trait_prob = PROBS["trait"][genes][has_trait]

        # 5. Moltiplica per accumulare la probabilità congiunta
        joint_prob *= (gene_prob * trait_prob)

    return joint_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # 1. Determina il numero di geni della persona in questo scenario
        if person in one_gene:
            genes = 1
        elif person in two_genes:
            genes = 2
        else:
            genes = 0
            
        # 2. Determina se la persona manifesta il tratto in QUESTO scenario
        has_trait = person in have_trait
        
        # 3. Aggiunge 'p' al secchiello corrispondente per il gene
        probabilities[person]["gene"][genes] += p
        
        # 4. Aggiunge 'p' al secchiello corrispondente per il tratto
        probabilities[person]["trait"][has_trait] += p



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        
        # --- NORMALIZZA I GENI ---
        # 1. Calcola la somma di tutti i valori attuali per i geni (0, 1 e 2)
        gene_sum = sum(probabilities[person]["gene"].values())
        
        # 2. Dividi ogni valore per la somma totale
        for gene_count in range(3):
            probabilities[person]["gene"][gene_count] /= gene_sum
            
            
        # --- NORMALIZZA I TRATTI ---
        # 1. Calcola la somma di tutti i valori attuali per i tratti (True e False)
        trait_sum = sum(probabilities[person]["trait"].values())
        
        # 2. Dividi ogni valore per la somma totale
        for has_trait in [True, False]:
            probabilities[person]["trait"][has_trait] /= trait_sum


if __name__ == "__main__":
    main()

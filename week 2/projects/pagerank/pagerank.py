
import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    prob_dist = {}
    total_pages = len(corpus)

    #case o linkk
    if len(corpus[page]) == 0:
        for p in corpus: #prende tutte le pages 
            prob_dist[p] = 1/total_pages
        return prob_dist
    
    #case links != 0
    #definiamo probabilità random 
    prob_random = ( 1 - damping_factor)/total_pages

    #def probabil reltiva ai link (divisa per il numero di pagine legate dai link)
    prob_link = damping_factor/(len(corpus[page]))

    # dobbiamo assegnare la probabiblità a tutte le pagine del corpus
    for p in corpus :
        prob_dist[p] = prob_random
        if p in corpus[page]:
            prob_dist[p] += prob_link #aggiunge prob_link a quella randomica gia presente

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #inizializzazione conteggio, lo impostiamo per ogni pagina di corpus

    pagerank_counts = {} #dizionario vuoto, chiavi = pagine, valori = contatore
    for page in corpus:
        pagerank_counts[page] = 0

    #inizio con il primo campione, scelto random
    current_page =random.choice(list(corpus.keys())) #estrazione randomia
    pagerank_counts[current_page] += 1               #aggiorna il contatore della pagina

    #ora si inizia a campionare n-1 volte

    for i in range(n-1):
        #richiamare la funzione transition per ottenere la probabil di dist.
        prob_dist = transition_model(corpus, current_page, damping_factor)

        #ora dobbiamo effettuare la nuova scelta randomica, prima però va pesata la scelta
        #separazione tra pagine e relative probabilità
        pages = list(prob_dist.keys()) #ricorda keys estrae dal dizionario
        probabilities = list(prob_dist.values())

        #scelta randomica pesata
        next_page = random.choices(population = pages, weights = probabilities, k = 1)[0]

        #aggiorno conteggio
        pagerank_counts[next_page] += 1

        #aggiorno current page
        current_page = next_page

        # conteggio finale, ad ogni pagina è associato un count ->
        #alla fine bisogna restituire un dizionario con chiavi le pagine e i valori stimati-> dizionario page rank
    final_pagerank = {}
    for page in pagerank_counts:
        final_pagerank[page] = pagerank_counts[page]/n 

    return final_pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    
    pageranks = { page: 1/N for page in corpus}

    #iniziamo l'iterazione
    while True:
        new_pageranks = {} # nuovo dizionario con i valori aggiornati all'interno del ciclo

        max_change = 0 #inizializzazione criterio d'arresto

        # ora andiamo a calcolare il pr per ogni pagina P del corpus
        for p in corpus:
            sumlinks = 0 #partiamo da un valore nullo e lo aggiorniamo all'interno del ciclo per i
            
            #ora consideriamo le i pagine che linkano la pagina p
            for i in corpus:
                #se P è presente nella pagina i allora è linkata
                if p in corpus[i]:
                    sumlinks += pageranks[i]/len(corpus[i])
                
                elif len(corpus[i]) == 0: # condizione in cui i non linki p
                    sumlinks += pageranks[i] / N #come se linkassse tutti

            #definiamo random prob e link prob
            random_prob = (1 - damping_factor)/N
            link_prob = damping_factor*sumlinks
            new_pageranks[p] = random_prob + link_prob

            #analizziamo la differenza ottenuta con 'literazione, per ogni pagina p
            change = abs( new_pageranks[p] - pageranks[p] )
            if change > max_change:
                max_change = change
        
        #sostituiamo i vecchi PR[p] con i nuovi
        pageranks = new_pageranks.copy()

        
        #condizione d'arresto:
        if max_change <= 0.001:
            break

    return pageranks

if __name__ == "__main__":
    main()

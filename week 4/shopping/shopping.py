import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    #prima di entrare nel ciclo mappiamo i mesi
    mesi = {
        "Jan": 0, "Feb": 1, "Mar": 2, "Apr": 3,
        "May": 4, "June": 5, "Jul": 6, "Aug": 7,
        "Sep": 8, "Oct": 9, "Nov": 10, "Dec": 11
    }

    #carichiamo i dati dal file CSV
    with open(filename, mode = "r") as f:
        reader =  csv.DictReader(f)
        #caricati i dati riga per riga ora iniziamo con la conversione dei dati in evidence e labels
        for row in reader:
            #creiamo uan lista temporanea per l'evidence
            temp_evidence = []
            #aggiungiamo i valori convertiti in base al tipo di dato richiesto
            temp_evidence.append(int(row["Administrative"]))        
            temp_evidence.append(float(row["Administrative_Duration"]))
            temp_evidence.append(int(row["Informational"]))
            temp_evidence.append(float(row["Informational_Duration"]))      
            temp_evidence.append(int(row["ProductRelated"]))
            temp_evidence.append(float(row["ProductRelated_Duration"]))
            temp_evidence.append(float(row["BounceRates"]))
            temp_evidence.append(float(row["ExitRates"]))
            temp_evidence.append(float(row["PageValues"]))
            temp_evidence.append(float(row["SpecialDay"]))
            temp_evidence.append(mesi[row["Month"]]) #convertiamo il mese in indice
            temp_evidence.append(int(row["OperatingSystems"]))
            temp_evidence.append(int(row["Browser"]))
            temp_evidence.append(int(row["Region"]))
            temp_evidence.append(int(row["TrafficType"]))
            #convertiamo VisitorType in 0 o 1  
            if row["VisitorType"] == "Returning_Visitor":
                temp_evidence.append(1)
            else:
                temp_evidence.append(0)
            #convertiamo Weekend in 0 o 1
            if row["Weekend"] == "TRUE":
                temp_evidence.append(1)
            else:
                temp_evidence.append(0)
            #aggiungiamo la lista temporanea all'evidence   
            # aggiungiamo la label corrispondente
            evidence.append(temp_evidence)
            if row["Revenue"] == "TRUE":
                labels.append(1)
            else:
                labels.append(0)        

    return (evidence, labels)   



def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    #inizializzazione del modello:
    model = KNeighborsClassifier(n_neighbors=1)
    #addestramento del modello:
    model.fit(evidence, labels)
    return model    

    


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    # inizializzazione contatori:
    tot_real_pos = 0
    tot_real_neg = 0
    tot_pred_pos = 0
    tot_pred_neg = 0

    # ovviamente Labels e prediction hanno la stessa dimensione
    #effettuiamo il conteggio all'interno dei cicli for:
    for i in range(len(labels)):
        if labels[i] == 1:
            tot_real_pos +=1
            if predictions[i] == 1:
                tot_pred_pos +=1
        elif labels[i] == 0:
            tot_real_neg +=1
            if predictions[i] == 0:
                tot_pred_neg +=1

    #calcoolo sensitivity e specificity
    sensitivity = tot_pred_pos/tot_real_pos
    specificity = tot_pred_neg/tot_real_neg
    return (sensitivity, specificity)
    
    


if __name__ == "__main__":
    main()

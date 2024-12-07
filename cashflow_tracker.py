import pandas as pd
import configparser

from datetime import date
from datetime import datetime
from cashflow import Cashflow


config = configparser.ConfigParser()
# Lettura del file settings.ini
config.read('settings.ini', encoding='utf-8')
# Accesso alle impostazioni
cashflow_file_path = config['SETTINGS']['cashflow_file_path']
income_category = config['LIST']['income_category'].split(",")
expense_category = config['LIST']['expense_category'].split(",")
cashflow_category = expense_category + income_category
actions = config['LIST']['actions'].replace('_',' ').split(",")
summary_type = config['LIST']['summary_type'].replace('_',' ').split(",")


def main():
   print(f"📌 Eseguendo il tracker.")
   df = open_db(cashflow_file_path)
   
   while True:

        # Far scegliere all'utente le operazioni da effettuare
        selected_action = choose_from_list(actions)

        if selected_action == " Esci":
            print("📌 Chiusura programma")  
            save_df_to_file(df ,cashflow_file_path)
            break  
        

        elif selected_action == " Registrazione movimenti":
            # Far inserire all'utente i movimenti
            df = get_user_cashflow(df)      


        elif selected_action == " Visualizzare resoconto":
            # Far scegliere periodo e tipo di resoconto
            
            # Leggere il file e fare un resoconto   
            summarize_cashflow(df,cashflow_file_path)
            input("Premere invio per tornare al menú principale")


        elif selected_action == " Modificare registrazioni":
            # Permettere di modificare le registrazioni fatte
            pass


        elif selected_action == " Impostazioni":
            # Permettere di scegliere determinati parametri nelle impostazioni
            # Salvarli su un fili .ini
            pass

# Carica il file csv sul df pandas
def open_db(file_path):
    try:
        df = pd.read_csv(file_path)
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
        print("📌 Dati caricati correttamente.")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Data", "Causale", "Categoria", "Importo"])
        print("📌 File non trovato. Creato nuovo database vuoto.")
    return df

# Verifica che la categoria inserita sia nella lista income_category
def in_income_cat(category):
    result = True if category in income_category else False
    return result

# Fa scegliere l'utente dalla lista inserita e restituisce direttamente la categoria scelta
def choose_from_list(base_list):
    # Clearare la console
    print("\033c", end="")

    while True:
        print("Scegli una categoria dalla lista: ")
        for i, category_name in enumerate(base_list):
            print(f"   {i +1}. {category_name}")
        
        value_range = f"[1 - {len(base_list)}]"
        try:
            selected_index = int(input(f"Inserisci un numero tra {value_range}: ")) - 1
        except ValueError:
            print("É richiesto l'inserimento di un numero, riprova.")
            continue
                
        if selected_index in range(len(base_list)): 
            selected_category = base_list[selected_index]

            # Clearare la console
            print("\033c", end="")

            return selected_category
        else:
            print("Riprova inserendo un valore valido.")
    
# Fa inserire l'anno e verifica sia inserito correttamente
def get_year():
    while True:
        user_year = input("Inserire anno di riferimento:")

        try:
            if len(user_year) == 4:  # Anno in formato YYYY
                year = datetime.strptime(user_year, "%Y").year
            elif len(user_year) == 2:  # Anno in formato YY
                year = datetime.strptime(user_year, "%y").year
            else:
                raise ValueError("Formato non valido! Inserisci la data nel formato YYYY o YY")
            break
        except ValueError:
            print("Formato non valido! Inserisci la data nel formato YYYY o YY")
    return year

# Fa inserire il mese e verifica si inserito correttamente
def get_month():
    while True:
        user_month = input("Inserire mese di riferimento:")

        try:
            month = datetime.strptime(user_month, "%m").month
            break
        except ValueError:
            print("Formato non valido! Inserisci la data nel formato MM")
    return month

# Fa inserire tutti i dati di una registrazione e aggiunge la registrazione al df
def get_user_cashflow(df):
    print(f"📌 Ricevendo informazioni spese.")
    
    # Selezione data
    while True:
        cashflow_date = input("Inserisci la data del movimento(gg/mm/aaaa): ")
        try:
            cashflow_date = datetime.strptime(cashflow_date, "%d/%m/%Y")
            cashflow_date = cashflow_date.strftime ("%d/%m/%Y")
            break
        except ValueError:
            print("Formato della data non valido! Riprova usando il formato gg/mm/aaaa.")

    # Selezione della categoria trmite la funzione choose_from_list       
    selected_category = choose_from_list(cashflow_category)

    # Selezione causale e ammontare
    cashflow_name = input("Inserisci la causale del movimento: ")
    cashflow_amount = float(input("Inserisci l'ammontare del movimento: "))
    cashflow_amount = abs(cashflow_amount) if in_income_cat(selected_category) else -abs(cashflow_amount)
    # cashflow_amount = abs(cashflow_amount) if in_income_cat(cashflow_category[selected_index]) else -abs(cashflow_amount)

    new_cashflow = Cashflow(
        Data=cashflow_date, Causale=cashflow_name, Categoria=selected_category, Importo=cashflow_amount
    )
    df = pd.concat([df,pd.DataFrame([vars(new_cashflow)])], ignore_index=True)
    return df

# Salva il df pandas inserito nel file csv
def save_df_to_file(df,file_path):
    print(f"📌 Salvando movimenti finanziari su {file_path}")
    df.to_csv(file_path, index=False)

# Restituisce un resoconto per categoria del file csv
def summarize_cashflow(df,cashflow_file_path):
    l = [" Mensile", " Annuale"]
    
    chosen_summary = choose_from_list(summary_type)
    if chosen_summary == " Per categoria":
        print(df.groupby('Categoria').agg(
            Totale = ('Importo', 'sum'),
            Operazioni = ('Importo', 'count')
        ))
        
    elif chosen_summary == " Movimenti":
        period = choose_from_list(l)
        if period == " Annuale":
            year = get_year()
            print(df[df['Data'].dt.year == year])
        else:
            year = get_year()
            month = get_month()
            print(df[
                (df['Data'].dt.year == year) & (df['Data'].dt.month == month)])
         
    
            



if __name__ == "__main__":
    main()


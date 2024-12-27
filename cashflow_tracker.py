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



def main():
   print(f"📌 Eseguendo il tracker.")
   df = open_db(cashflow_file_path)

   while True:
        print("\033c", end="")    
        # Fa scegliere all'utente le operazioni da effettuare
        selected_action = choose_from_list(actions)

        if selected_action == " Esci":
            print("📌 Chiusura programma")  
            df = df.sort_values(by = 'Data')
            save_df_to_file(df ,cashflow_file_path)
            break  
        

        elif selected_action == " Registrazione movimenti":
            # Fa inserire all'utente i movimenti
            df = get_user_cashflow(df)      


        elif selected_action == " Visualizzare resoconto":
            # Legge il file e fa un resoconto in base alle scelte dell'utente  
            summarize_cashflow(df,cashflow_file_path)


        elif selected_action == " Modificare registrazioni":
            # Fa modificare i movimenti inseriti
            df = modify_cashflow(df)
            pass


        elif selected_action == " Impostazioni":
            #TODO: Permettere di scegliere determinati parametri nelle impostazioni e aggiornarli sul file settings.ini
            pass

# Carica il file csv sul df pandas
def open_db(file_path):
    try:
        df = pd.read_csv(file_path, dayfirst=True)
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
        user_year = input("Inserire anno di riferimento: ")

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
        user_month = input("Inserire mese di riferimento: ")

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
            # Convalida formato data, converte da str a datetime e poi riporta a str
            cashflow_date = datetime.strptime(cashflow_date, "%d/%m/%Y")
            break
        except ValueError:
            print("Formato della data non valido! Riprova usando il formato gg/mm/aaaa.")

    # Selezione della categoria trmite la funzione choose_from_list       
    selected_category = choose_from_list(cashflow_category)

    # Selezione causale e ammontare
    cashflow_name = input("Inserisci la causale del movimento: ")
    cashflow_amount = float(input("Inserisci l'ammontare del movimento: "))
    cashflow_amount = abs(cashflow_amount) if in_income_cat(selected_category) else -abs(cashflow_amount)

    new_cashflow = Cashflow(
        Data=cashflow_date, Causale=cashflow_name, Categoria=selected_category, Importo=cashflow_amount
    )
    df = pd.concat([df,pd.DataFrame([vars(new_cashflow)])], ignore_index=True)
    return df

# Salva il df pandas inserito nel file csv
def save_df_to_file(df,file_path):
    print(f"📌 Salvando movimenti finanziari su {file_path}")
    df['Data'] = df['Data'].dt.strftime('%d/%m/%Y')
    df.to_csv(file_path, index=False)

# Restituisce un resoconto per categoria del file csv
def summarize_cashflow(df,cashflow_file_path):
    l = [" Annuale", " Mensile"]
    month = {
        '01': 'Gen', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'Mag', 
        '06': 'Giu', '07': 'Lug', '08': 'Ago', '09': 'Set', '10': 'Ott', 
        '11': 'Nov', '12': 'Dic'
    }

    # Ottengo l'anno in corso
    current_year =  datetime.now().year
    # Stampa una DASHBOARD con il resoconto dell'anno corrente o degli ultimi 12 mesi o meno 
    #REVIEW:resoconto con le seguenti voci: ENTRATE, USCITE, 
    df_current_year = df[df['Data'].dt.year == current_year]
    df_summary = df_current_year.copy()
    df_summary['Mese'] = df_summary['Data'].dt.strftime('%m').map(month)
    df_summary['Tipo'] = df_summary['Categoria'].apply(lambda x: 'Entrate' if x in income_category else 'Uscite')
    df_summary = df_summary.groupby(['Mese','Tipo'])['Importo'].sum().unstack(fill_value=0)
    # .unstuck trasforma le righe Entrate e Uscite in colonne mentre .T fa la trasposizione della tabella
    df_summary = df_summary.T
    print(df_summary)
    print('')

    # Fa inserire un input dall'utente    
    while True:
        chosen_summary= input("Inserisci: \n Invio  - Esci \n   0    - Visualizza movimenti \n 1 / 12 - Visualizza resoconto mensile\n")
        if chosen_summary == "":
            break 
        if chosen_summary.isdigit():  # Verifica che l'input sia composto solo da cifre
            numero = int(chosen_summary)
            if 0 <= numero <= 12:    
                break
        print('Input non valido, riprova.')
    print("\033c", end="") 

    # Se vuoto torna al menú        
    if chosen_summary == '':
        pass
        
    # Se 0 permette di vedere direttamente i movimenti        
    elif int(chosen_summary) == 0:
        period = choose_from_list(l)
        if period == " Annuale":
            year = get_year()
            df_summary = df[df['Data'].dt.year == year].copy()
            df_summary['Data'] = df_summary['Data'].dt.strftime('%d-%m-%Y')
            print(df_summary)
            input("\nPremere invio per tornare al menú principale")
        else:
            year = get_year()
            month = get_month()
            df_summary = df[(df['Data'].dt.year == year) & (df['Data'].dt.month == month)].copy()
            df_summary['Data'] = df_summary['Data'].dt.strftime('%d-%m-%Y')
            print(df_summary)
            input("\nPremere invio per tornare al menú principale")
    
    #TODO: Se tra 1 e 12 mostra il dettaglio del mese
    elif 1 <= int(chosen_summary) <= 12:
        df_summary = df[(df['Data'].dt.year == current_year) & (df['Data'].dt.month == int(chosen_summary))].copy()
        df_summary['Tipo'] = df_summary['Categoria'].apply(lambda x: 'Entrate' if x in income_category else 'Uscite')
        print('Entrete')
        print(df_summary[df_summary['Tipo'] == 'Entrate'].groupby('Categoria')['Importo'].sum())
        print('\nUscite')
        print(df_summary[df_summary['Tipo'] == 'Uscite'].groupby('Categoria')['Importo'].sum())    
        input("\nPremere invio per tornare al menú principale")        

    #TODO: aggiungere dei grafici alla DASHBOARD
    #TODO: aggiungere dei grafici al resoconto mensile    
    #TODO: Suddivisione tra spese necessarie e non        

# Permette di modificare i movimenti inseriti
def modify_cashflow(df):
   # Far segliere se stampre l'elenco movimenti per mese o per anno
   # Stampre elenco movimenti con indice davanti in base alla precedente scelta
   # Far selezionare l'indice del movimento da modificare
      
    period = choose_from_list([" Annuale"," Mensile"])
    if period == " Annuale":
        year = get_year()
        df_filtered = df.loc[df['Data'].dt.year == year]

        # Visualizza le righe filtrate con l'indice personalizzato
        df_filtered_display = df_filtered.copy()
        df_filtered_display['Data'] = df_filtered_display['Data'].dt.strftime('%d-%m-%Y')
        df_filtered_display.index = range(1, len(df_filtered_display) + 1)
        print(df_filtered_display)

        # Richiesta dell'indice da modificare
        while True:
            try:
                chosen_index = int(input("Inserire l'indice del movimento da modificare: "))
                if chosen_index in df_filtered_display.index:
                    break
            except ValueError:
                pass        

        # Converte l'indice della visualizzazione all'indice effettivo del df
        chosen_index = df_filtered_display.index.get_loc(chosen_index)            

    else:
        year = get_year()
        month = get_month()

        df_filtered = df[(df['Data'].dt.year == year) & (df['Data'].dt.month == month)]

        # Visualizza le righe filtrate con l'indice personalizzato
        df_filtered_display = df_filtered.copy()
        df_filtered_display['Data'] = df_filtered_display['Data'].dt.strftime('%d-%m-%Y')
        df_filtered_display.index = range(1, len(df_filtered_display) + 1)
        print(df_filtered_display)

        # Richiesta dell'indice da modificare
        while True:
            try:
                chosen_index = int(input("Inserire l'indice del movimento da modificare: "))
                if chosen_index in df_filtered_display.index:
                    break
            except ValueError:
                pass        

        # Converte l'indice della visualizzazione all'indice effettivo del df
        chosen_index = df_filtered_display.index.get_loc(chosen_index) 
            
    # Far scegliere quale campo modificare o se eliminare il movimento
    print("\033c", end="")
    print("Movimento scelto: ")
    print(df_filtered.loc[chosen_index])
    chosen_action = choose_from_list([
        " Modifica data"," Modifica causale"," Modifica categoria"," Modifica importo"," Elimina registrazione"," Esci"
        ])
          
    # Comportarsi di conseguenza
    if chosen_action == " Modifica data":
        while True:
            modified_date = input("Inserisci la data del movimento(gg/mm/aaaa): ")
            try:
                # Convalida formato data, converte da str a datetime
                modified_date = datetime.strptime(modified_date, "%d/%m/%Y")
                break
            except ValueError:
                print("Formato della data non valido! Riprova usando il formato gg/mm/aaaa.")

        df.at[df_filtered.index[chosen_index], "Data"] = modified_date
        return df   
    
    elif chosen_action == " Modifica causale":
        df.at[df_filtered.index[chosen_index], "Causale"] = input("Inserisci nuova causale: ")
        return df

    elif chosen_action == " Modifica categoria":
        chosen_category = choose_from_list(cashflow_category)
        initial_category = df.at[df_filtered.index[chosen_index], "Categoria"]
        df.at[df_filtered.index[chosen_index], "Categoria"] = chosen_category
        if chosen_category != initial_category:
            if chosen_category in income_category: 
                df.at[df_filtered.index[chosen_index], "Importo"] = abs(df.at[df_filtered.index[chosen_index], "Importo"])
            else:
                df.at[df_filtered.index[chosen_index], "Importo"] = - abs(df.at[df_filtered.index[chosen_index], "Importo"])
        return df    
        

    elif chosen_action == " Modifica importo":
        modified_amount = float(input("Inserisci l'ammontare del movimento: "))
        # Se la categoria del movimento originale fa parte delle entrate registara la variazione positiva altrimenti negativa
        modified_amount = abs(modified_amount) if in_income_cat(df.at[df_filtered.index[chosen_index],"Categoria"]) else -abs(modified_amount)

        df.at[df_filtered.index[chosen_index], "Importo"] = modified_amount
        return df

    elif chosen_action == " Elimina registrazione":
        df_new = df.drop(chosen_index)
        if period == " Annuale":
            df_filtered = df_new.loc[df_new['Data'].dt.year == year]
        else:
            df_filtered = df_new[(df_new['Data'].dt.year == year) & (df_new['Data'].dt.month == month)]

        # Visualizza le righe filtrate con l'indice personalizzato
        df_filtered_display = df_filtered.copy()
        df_filtered_display['Data'] = df_filtered_display['Data'].dt.strftime('%d-%m-%Y')
        df_filtered_display.index = range(1, len(df_filtered_display) + 1)
        print(df_filtered_display)
        print('Mantenere la modifica effettuata?')
        confirm = choose_from_list([' Sì',' No'])
        if confirm == ' Sì':
            return df_new
        
    elif chosen_action == " Esci":
        return df
        
    


if __name__ == "__main__":
    main()


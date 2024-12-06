class Cashflow:

    def __init__(self, Data, Causale, Categoria, Importo) -> None:
        self.Data = Data
        self.Causale = Causale
        self.Categoria = Categoria
        self.Importo = Importo
    
    def __repr__(self):
        return f"-->Cashflow: {self.Data}, {self.Causale}, {self.Categoria}, €{self.Importo:.2f}<--"
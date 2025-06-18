class DispositivoInteligente:
    """
    Representa um dispositivo elétrico individual na casa, como uma lâmpada ou um ar condicionado.
    """
    # O método __init__ é o "construtor" da classe. Ele é chamado toda vez que um novo
    # objeto DispositivoInteligente é criado.
    def __init__(self, nome, consumo_watts, prioridade=1):
        # Atributos são as variáveis que pertencem a cada objeto.
        self.nome = nome  # Um nome amigável para o dispositivo (ex: "Luz da Cozinha").
        self.consumo_watts = float(consumo_watts)  # A potência que o dispositivo consome quando está ligado.
        self.esta_ligado = False  # O estado inicial de qualquer dispositivo é sempre desligado.
        self.prioridade = prioridade  # Define a importância do dispositivo. Usado na automação.
                                      # Níveis de Prioridade: 1 = Essencial, 2 = Média, 3 = Baixa (pode ser desligado para economizar energia).

    def ligar(self):
        """Muda o estado do dispositivo para ligado."""
        # A verificação 'if not self.esta_ligado' previne que o código execute
        # ações desnecessárias se o dispositivo já estiver ligado.
        if not self.esta_ligado:
            self.esta_ligado = True
            # O 'print' serve como um log no terminal, útil para debugar e ver o que está acontecendo.
            print(f"  -> Dispositivo '{self.nome}' foi LIGADO.")
        return self.esta_ligado  # Retorna o novo estado do dispositivo.

    def desligar(self):
        """Muda o estado do dispositivo para desligado."""
        if self.esta_ligado:
            self.esta_ligado = False
            print(f"  -> Dispositivo '{self.nome}' foi DESLIGADO.")
        return self.esta_ligado


class Bateria:
    """
    Simula uma bateria de armazenamento de energia, com lógica para carregar e descarregar.
    """
    def __init__(self, capacidade_kwh, carga_inicial_kwh=0):
        # A capacidade total de armazenamento da bateria, em kiloWatt-hora (kWh).
        self.capacidade_kwh = float(capacidade_kwh)
        # A quantidade de energia que a bateria tem no momento em que é criada.
        self.carga_atual_kwh = float(carga_inicial_kwh)
        # O estado atual da bateria, útil para exibir no dashboard.
        self.estado = "Ociosa"  # Pode ser "Carregando", "Descarregando", "Ociosa".

    # O '@property' é um "decorador" do Python que transforma um método em um atributo
    # que é "somente leitura". Isso permite que acessemos 'bateria.porcentagem_carga'
    # como uma variável, mas seu valor é calculado toda vez que é acessado.
    @property
    def porcentagem_carga(self):
        """Calcula e retorna a porcentagem da carga atual da bateria."""
        # Verificação de segurança para evitar um erro de divisão por zero se a bateria tiver capacidade 0.
        if self.capacidade_kwh == 0:
            return 0
        # A fórmula padrão de porcentagem.
        return (self.carga_atual_kwh / self.capacidade_kwh) * 100

    def carregar(self, watts, segundos):
        """Adiciona energia à bateria com base em uma potência (watts) aplicada por um tempo (segundos)."""
        # A simulação roda em passos de 1 segundo. Esta fórmula converte a potência aplicada
        # nesse segundo para a unidade de armazenamento da bateria (kWh).
        # (Watts * segundos) = Joules. Joules / 3600 = Watt-hora. Watt-hora / 1000 = kWh.
        energia_kwh = (watts * segundos) / 3600 / 1000
        
        # Adiciona a energia calculada à carga atual.
        # A função 'min()' garante que a carga nunca ultrapasse a capacidade máxima da bateria.
        self.carga_atual_kwh = min(self.capacidade_kwh, self.carga_atual_kwh + energia_kwh)
        self.estado = "Carregando" # Atualiza o estado para refletir a ação.

    def descarregar(self, watts, segundos):
        """Remove energia da bateria para alimentar a casa."""
        # A mesma lógica de conversão de energia da função 'carregar'.
        energia_kwh = (watts * segundos) / 3600 / 1000
        
        # Remove a energia da carga atual.
        # A função 'max()' garante que a carga da bateria nunca fique negativa (abaixo de 0).
        self.carga_atual_kwh = max(0, self.carga_atual_kwh - energia_kwh)
        self.estado = "Descarregando"
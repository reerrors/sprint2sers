# Importa as bibliotecas necessárias para o projeto.
import time  # Para pausas (time.sleep)
import threading  # Para executar a simulação e o servidor web ao mesmo tempo
import math  # Para cálculos matemáticos (seno, na simulação solar)
from datetime import datetime  # Para trabalhar com datas e horas (não usado diretamente, mas bom ter)
from flask import Flask, render_template, jsonify, request  # Para criar o servidor web e o dashboard

# Importa as classes que definimos no nosso outro arquivo, 'modelos.py'.
# Isso mantém o código organizado, separando os dados da lógica da aplicação.
from modelos import DispositivoInteligente, Bateria


# --- 1. GERENCIADOR DE ESTADO GLOBAL E LÓGICA PRINCIPAL ---

# Cria uma "fechadura" (lock) para os dados. Como a simulação e o servidor web (Flask)
# rodam em threads separadas, o RLock garante que elas não tentem modificar os
# mesmos dados ao mesmo tempo, o que causaria erros. RLock (Re-entrant Lock)
# permite que a mesma thread "pegue a chave" várias vezes, evitando deadlocks.
data_lock = threading.RLock()

class GerenciadorEnergia:
    """
    A classe principal que age como o cérebro do sistema.
    Ela controla todos os componentes, executa a lógica da simulação
    e mantém o estado atual de tudo.
    """
    def __init__(self):
        # Inicializa a bateria do sistema com 10 kWh de capacidade e 5 kWh de carga inicial (50%).
        self.bateria = Bateria(capacidade_kwh=10, carga_inicial_kwh=5)

        # Cria um dicionário para armazenar os objetos dos dispositivos inteligentes.
        # A chave (ex: "luz_cozinha") é um ID interno, e o valor é o objeto DispositivoInteligente.
        self.dispositivos = {
            "luz_cozinha": DispositivoInteligente("Luz da Cozinha", 60, prioridade=1), # Prioridade 1 = essencial
            "geladeira": DispositivoInteligente("Geladeira", 150, prioridade=1),      # Prioridade 1 = essencial
            "ar_condicionado": DispositivoInteligente("Ar Condicionado", 1500, prioridade=3) # Prioridade 3 = não essencial
        }
        # Inicia o sistema com a geladeira já ligada, pois é um aparelho essencial.
        self.dispositivos["geladeira"].ligar()
        
        # Variáveis para armazenar o estado atual da energia
        self.geracao_solar = 0
        self.consumo_rede = 0
        self.alerta_global = None  # Guarda mensagens de alerta para o dashboard

    def get_consumo_casa_total(self):
        """Soma o consumo de todos os dispositivos que estão atualmente ligados."""
        return sum(d.consumo_watts for d in self.dispositivos.values() if d.esta_ligado)

    def simular_geracao_solar(self):
        """
        Simula a geração de energia solar.
        Cria uma curva de geração que se parece com a de um dia real (fraca de manhã/noite, forte ao meio-dia).
        O ciclo completo de um "dia" aqui dura 240 segundos (4 minutos) para fins de demonstração.
        """
        ciclo = (time.time() % 240) / 240  # Valor que vai de 0.0 a 1.0 a cada 4 minutos
        # A função seno cria uma curva suave de geração, com pico máximo de 3000W.
        self.geracao_solar = max(0, 3000 * math.sin(ciclo * math.pi))

    def run_simulation_step(self):
        """
        Este é o coração da simulação. Esta função é chamada repetidamente (a cada segundo)
        para calcular o balanço de energia e tomar decisões.
        """
        # "with data_lock:" garante que nenhuma outra parte do programa (como o Flask)
        # possa ler ou escrever nos dados enquanto estamos no meio de um cálculo.
        with data_lock:
            self.simular_geracao_solar()
            consumo_casa = self.get_consumo_casa_total()
            
            # Calcula o saldo de energia: positivo se há sobra, negativo se há falta.
            saldo_energia = self.geracao_solar - consumo_casa
            
            if saldo_energia > 0:  # Se há mais geração do que consumo...
                self.bateria.carregar(saldo_energia, 1) # Carrega a bateria com a energia que sobrou.
                self.consumo_rede = 0  # Não precisa usar a rede elétrica.
            else:  # Se há mais consumo do que geração...
                energia_necessaria = abs(saldo_energia)
                
                # Verifica se a bateria pode ajudar e se tem mais de 20% de carga.
                if self.bateria.carga_atual_kwh > 0 and self.bateria.porcentagem_carga > 20:
                    # Usa a energia da bateria para abater a necessidade.
                    energia_fornecida_pela_bateria = min(energia_necessaria, self.bateria.carga_atual_kwh * 3600 * 1000)
                    self.bateria.descarregar(energia_fornecida_pela_bateria, 1)
                    energia_necessaria -= energia_fornecida_pela_bateria
                else:
                    self.bateria.estado = "Ociosa" # Bateria não pode ajudar.
                
                # O que ainda faltar de energia depois da ajuda da bateria, puxa da rede.
                self.consumo_rede = energia_necessaria

            # --- FUNCIONALIDADE AUTOMATIZADA: PRIORIZAÇÃO DE CONSUMO ---
            # Se a bateria está baixa (< 20%) e ainda estamos consumindo da rede,
            # o sistema toma uma decisão para economizar energia.
            if self.bateria.porcentagem_carga < 20 and self.consumo_rede > 0:
                self.alerta_global = f"ALERTA: Bateria com {self.bateria.porcentagem_carga:.1f}%. Desligando aparelhos não essenciais."
                # Procura por todos os dispositivos que não são essenciais (prioridade > 1) e os desliga.
                for dev in self.dispositivos.values():
                    if dev.prioridade > 1 and dev.esta_ligado:
                        dev.desligar()
            else:
                self.alerta_global = None  # Se a condição não se aplica, limpa o alerta.

    def get_estado_api(self):
        """Prepara e retorna um dicionário com todos os dados atuais do sistema."""
        with data_lock:
            # Cria uma cópia segura dos dados para ser enviada ao dashboard via JSON.
            dispositivos_api = [
                {"id": dev_id, "nome": dev.nome, "esta_ligado": dev.esta_ligado}
                for dev_id, dev in self.dispositivos.items()
            ]
            
            return {
                "bateria_porcentagem": self.bateria.porcentagem_carga,
                "bateria_estado": self.bateria.estado,
                "dispositivos": dispositivos_api,
                "geracao_solar": self.geracao_solar,
                "consumo_casa": self.get_consumo_casa_total(),
                "consumo_rede": self.consumo_rede,
                "alerta": self.alerta_global
            }

# Cria a instância principal do nosso gerenciador. Ele será o objeto central da aplicação.
gerenciador = GerenciadorEnergia()


# --- 2. SERVIDOR WEB FLASK (VISUALIZAÇÃO E CONTROLE) ---
# Inicializa a aplicação Flask, que cuidará de toda a parte web.
app = Flask(__name__)

@app.route('/')
def index():
    """Esta rota responde quando alguém acessa a página principal (ex: http://127.0.0.1:5000)."""
    # 'render_template' carrega o arquivo 'index.html' da pasta 'templates' e o envia ao navegador.
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    """
    Esta é a nossa API. O JavaScript do dashboard chama esta rota a cada 2 segundos
    para pegar os dados mais recentes do sistema e atualizar os gráficos e textos.
    """
    # 'jsonify' converte o dicionário Python em um formato JSON, que o JavaScript entende.
    return jsonify(gerenciador.get_estado_api())

@app.route('/comando/<device_id>/<action>', methods=['POST'])
def handle_command(device_id, action):
    """
    Esta rota recebe os comandos de ligar/desligar dos botões do dashboard.
    Ex: uma chamada para /comando/ar_condicionado/ligar
    """
    with data_lock:
        if device_id in gerenciador.dispositivos:
            dispositivo = gerenciador.dispositivos[device_id]
            if action == 'ligar':
                dispositivo.ligar()
            elif action == 'desligar':
                dispositivo.desligar()
            else:
                return jsonify({"status": "erro", "mensagem": "Ação inválida"}), 400
            
            # Força uma atualização da simulação para refletir a mudança imediatamente no painel.
            gerenciador.run_simulation_step()
            return jsonify({"status": "sucesso", "device_name": dispositivo.nome, "new_state": dispositivo.esta_ligado})
    return jsonify({"status": "erro", "mensagem": "Dispositivo não encontrado"}), 404


# --- 3. EXECUÇÃO DA APLICAÇÃO ---

def run_simulation_loop():
    """
    Função alvo da nossa thread de simulação.
    Fica em um loop infinito, chamando a lógica de simulação a cada segundo.
    """
    while True:
        gerenciador.run_simulation_step()
        time.sleep(1) # Pausa de 1 segundo entre cada passo da simulação.

# O bloco a seguir só é executado quando rodamos o script diretamente (python app.py).
if __name__ == '__main__':
    # Cria e inicia a thread da simulação. 'daemon=True' significa que a thread
    # será encerrada automaticamente quando o programa principal fechar.
    simulation_thread = threading.Thread(target=run_simulation_loop, daemon=True)
    simulation_thread.start()
    
    print("-> Servidor de Simulação e Controle iniciado.")
    print("-> Acesse o dashboard em http://127.0.0.1:5000")
    
    # Inicia o servidor Flask, que ficará esperando por requisições do navegador.
    # debug=True faz com que o servidor reinicie automaticamente quando você salva uma alteração no código.
    app.run(host='0.0.0.0', port=5000, debug=True)
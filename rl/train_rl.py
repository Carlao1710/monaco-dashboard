import random
import numpy as np
from keras.models import Sequential  # type: ignore
from keras.layers import Dense, Input  # type: ignore
from rl.rl_environment import GameRoomEnvironment
import sys
import os

# Adiciona o diretório raiz ao caminho do sistema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rl.rl_environment import GameRoomEnvironment

# Configuração inicial
games = ["The Runner", "Day One", "Lava Rush", "Super Monaco"]
env = GameRoomEnvironment(games)

# Hiperparâmetros
state_size = 3  # Número de características no estado do jogador
action_size = len(games)  # Número de jogos disponíveis (ações)
episodes = 50  # Número total de episódios de treinamento
gamma = 0.95  # Fator de desconto para aprendizado futuro
epsilon = 1.0  # Probabilidade inicial de exploração
epsilon_decay = 0.995  # Taxa de decaimento de epsilon
epsilon_min = 0.01  # Valor mínimo para epsilon
batch_size = 32  # Tamanho do lote para treinamento

# Construção do modelo
def build_model(state_size, action_size):
    """
    Cria um modelo de rede neural para aprendizado por reforço.
    """
    model = Sequential()
    model.add(Dense(24, input_dim=state_size, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(action_size, activation='linear'))
    model.compile(optimizer='adam', loss='mse')
    return model

model = build_model(state_size, action_size)

def build_model(state_size, action_size):
    model = Sequential([
        Input(shape=(state_size,)),
        Dense(24, activation='relu'),
        Dense(24, activation='relu'),
        Dense(action_size, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# Memória para experiência de replay
replay_memory = []

# Treinamento
for episode in range(episodes):
    # Criação de um perfil de jogador aleatório
    player_profile = {
        "games_played": random.randint(0, 100),
        "avg_time": random.uniform(1, 10),
        "tickets_generated": random.randint(0, 500),
        "engagement": random.uniform(0.5, 1.5),
    }
    state = env.get_player_state(player_profile)

    for _ in range(50):  # Limite de interações por episódio
        # Escolha da ação (exploração ou exploração)
        if np.random.rand() <= epsilon:
            action = random.choice(range(action_size))  # Exploração
        else:
            q_values = model.predict(state.reshape(1, -1), verbose=0)
            action = np.argmax(q_values[0])  # Exploração

        # Obtenção da recompensa e próximo estado
        reward = env.simulate_reward(games[action], player_profile)
        next_state = state  # No exemplo atual, o estado permanece o mesmo

        # Armazenar a experiência na memória
        replay_memory.append((state, action, reward, next_state, False))
        if len(replay_memory) > 50:
            replay_memory.pop(0)  # Remover experiências mais antigas

        # Treinamento em lote
        if len(replay_memory) >= batch_size:
            batch = random.sample(replay_memory, batch_size)
            for s, a, r, ns, d in batch:
                target = r + (1 - d) * gamma * np.max(model.predict(ns.reshape(1, -1), verbose=0)[0])
                target_f = model.predict(s.reshape(1, -1), verbose=0)
                target_f[0][a] = target
                model.fit(s.reshape(1, -1), target_f, epochs=1, verbose=0)

        state = next_state

    # Atualizar epsilon (redução da exploração)
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

    # Log de progresso
    print(f"Treinamento do episódio {episode + 1}/{episodes} concluído. Epsilon: {epsilon:.4f}")

    if (episode + 1) % 10 == 0:
        print(f"Episódio {episode + 1}/{episodes}: Epsilon = {epsilon:.4f}")

# Salvar modelo treinado
model.save("rl/game_recommendation_model.h5")
print("Modelo treinado salvo como 'game_recommendation_model.h5'")

if model:
    print("Modelo treinado com sucesso. Pronto para salvar.")
else:
    print("Erro: Modelo não treinado corretamente.")
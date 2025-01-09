from keras.models import load_model # type: ignore
import numpy as np
from rl.rl_environment import GameRoomEnvironment
from keras.losses import MeanSquaredError  # type: ignore # Adicione isso para registrar `mse`

# Certifique-se de que a função de perda está registrada
mse = MeanSquaredError()

# Carregar modelo
model = load_model("rl/game_recommendation_model.h5", custom_objects={"mse": mse})
games = ["The Runner", "Day One", "Lava Rush", "Super Monaco"]
env = GameRoomEnvironment(games)

# Recomendação
def recommend_game(player_profile):
    state = env.get_player_state(player_profile)
    q_values = model.predict(state.reshape(1, -1), verbose=0)
    recommended_game = games[np.argmax(q_values[0])]
    return recommended_game

# Exemplo de uso
player_profile = {
    "games_played": 20,
    "avg_time": 5.5,
    "tickets_generated": 300,
    "engagement": 1.2,
}
print("Jogo recomendado:", recommend_game(player_profile))
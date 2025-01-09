import numpy as np

# Configuração do ambiente RL
class GameRoomEnvironment:
    def __init__(self, games):
        self.games = games  # Lista de jogos disponíveis

    def simulate_reward(self, game, player_profile):
        # Exemplo simples de recompensa
        engagement_factor = player_profile.get("engagement", 1)
        if game == "The Runner":
            return 10 * engagement_factor
        elif game == "Day One":
            return 8 * engagement_factor
        elif game == "Lava Rush":
            return 6 * engagement_factor
        elif game == "Super Monaco":
            return 12 * engagement_factor
        return 0

    def get_player_state(self, player_profile):
        return np.array([
            player_profile["games_played"],
            player_profile["avg_time"],
            player_profile["tickets_generated"],
        ])
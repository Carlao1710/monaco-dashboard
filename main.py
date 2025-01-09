import streamlit as st
from src.analysis import (
    analyze_growth,
    calculate_orders_by_event,
    calculate_top_heavy_users,
    calculate_top_users_event_summary,
    calculate_unique_order_values_by_event,
    project_client_metrics,
    process_json_data,
    calculate_game_distribution,
    calculate_tickets_by_game_and_month,
    calculate_tickets_by_level,
    calculate_event_summary_with_outside_events,
)
from src.data_loader import load_json_data

# Configuração do Streamlit
st.title("Análise e Projeções do GameRoom da Monaco")
st.write("Explore os dados de partidas, tickets e usuários do GameRoom e realize projeções com base nos clientes da Monaco.")

# Caminho dos dados
DATA_DIR = "data/"

# Carregando os dados
data = load_json_data(DATA_DIR)

if not data:
    st.error("Erro ao carregar os dados. Verifique os arquivos JSON.")
else:
    # Processando os dados
    game_histories = process_json_data(data.get("gamehistories", []), "game_histories")
    tickets = process_json_data(data.get("tickets", []), "tickets")
    users = process_json_data(data.get("users", []), "users")
    game_events = process_json_data(data.get("gameevents", []), "game_events")

    # Análise de crescimento
    st.header("Crescimento em 2024")
    try:
        games_per_month, total_tickets_amount, users_per_month = analyze_growth(game_histories, tickets, users)

        st.subheader("Partidas por Mês")
        st.line_chart(games_per_month)

        st.subheader("Total de Tickets por Mês (Valor Total)")
        st.line_chart(total_tickets_amount)

        st.subheader("Usuários por Mês")
        st.line_chart(users_per_month)
    except ValueError as ve:
        st.error(f"Erro na análise: {ve}")
    except Exception as e:
        st.error(f"Erro inesperado na análise: {e}")

    # Gráfico de distribuição de tickets por jogos
    st.header("Distribuição de Tickets por Jogos")
    try:
        game_ticket_distribution = calculate_game_distribution(tickets)
        st.bar_chart(game_ticket_distribution)
    except Exception as e:
        st.error(f"Erro ao calcular distribuição de tickets: {e}")

    # Gráfico de Tickets x Jogos x Meses
    st.header("Distribuição de Tickets por Jogos e Meses")
    try:
        tickets_by_game_and_month = calculate_tickets_by_game_and_month(tickets)
        st.line_chart(tickets_by_game_and_month)
    except Exception as e:
        st.error(f"Erro ao calcular tickets por jogos e meses: {e}")

    # Resumo de Tickets e Partidas por Evento
    st.header("Resumo de Tickets e Partidas por Evento")
    try:
        # Calcular resumo por evento com partidas e tickets fora dos eventos
        event_summary_df = calculate_event_summary_with_outside_events(game_histories, tickets, game_events)

        # Exibir a tabela no Streamlit
        st.write("Tabela com o total de partidas e tickets gerados durante cada evento, incluindo fora dos eventos:")
        st.dataframe(event_summary_df)
    except Exception as e:
        st.error(f"Erro ao calcular resumo por evento: {e}")

    # Resumo de Orders por Evento
    st.header("Resumo de Orders por Evento")
    try:
        # Processar dados de Orders
        orders = process_json_data(data.get("orders", []), "orders")

        # Calcular Orders por evento
        orders_summary_df = calculate_orders_by_event(orders, game_events)

        # Exibir a tabela no Streamlit
        st.write("Tabela com o total de Orders (pagamentos concluídos) gerados durante cada evento:")
        st.dataframe(orders_summary_df)
    except Exception as e:
        st.error(f"Erro ao calcular resumo de Orders por evento: {e}")

    # Resumo de Valores Únicos e Quantidade de Compras por Evento
    st.header("Resumo de Valores Únicos e Quantidade de Compras por Evento")
    try:
        # Processar dados de Orders
        orders = process_json_data(data.get("orders", []), "orders")

        # Calcular valores únicos de compras por evento
        unique_order_values_summary_df = calculate_unique_order_values_by_event(orders, game_events)

        # Exibir a tabela no Streamlit
        st.write("Tabela com os valores únicos de compras e a quantidade de compras feitas por evento:")
        st.dataframe(unique_order_values_summary_df)
    except Exception as e:
        st.error(f"Erro ao calcular valores únicos de compras por evento: {e}")
        
    # Seção: Heavy Users da Monaco
st.header("Top 30 Heavy Users da Monaco")
try:
    # Calcular os 30 principais heavy users
    top_heavy_users_df = calculate_top_heavy_users(game_histories, users)

    # Exibir a tabela no Streamlit
    st.write("Tabela com os 30 usuários com mais partidas:")
    st.dataframe(top_heavy_users_df)
except Exception as e:
    st.error(f"Erro ao calcular os heavy users: {e}")

    # Top 10 Heavy Users do Evento Natal
st.header("Top 10 Heavy Users do Evento Natal")
try:
    natal_event_name = "Campeonato Season 6 - Natal"
    natal_start_date = "2024-12-13"
    natal_end_date = "2024-12-24"

    # Calcular os top 10 heavy users durante o evento Natal
    top_users_natal_df = calculate_top_users_event_summary(
        game_histories,
        users,
        natal_event_name,
        natal_start_date,
        natal_end_date,
        top_n=10
    )

    # Exibir a tabela no Streamlit
    st.write(f"Tabela com os top 10 usuários durante o evento '{natal_event_name}':")
    st.dataframe(top_users_natal_df)
except Exception as e:
    st.error(f"Erro ao calcular os top heavy users do evento Natal: {e}")

# Projeções para clientes da Claro
# st.header("Projeções para a Claro")
# st.write("Realize projeções exclusivas para clientes da Claro com base nos dados históricos e estimativas.")

# claro_clients = st.number_input("Quantidade de Clientes da Claro", min_value=1, value=40000, step=1)
# claro_percentage = st.number_input("Percentual de Clientes que Jogarão (%)", min_value=1, max_value=100, value=30, step=1)
# claro_weeks = st.number_input("Duração da Gamificação para Claro (semanas)", min_value=1, value=8, step=1)

# Seleção de jogos para projeções da Claro
# claro_game_choices = ["The Runner", "Day One", "Lava Rush", "Super Monaco"]
# claro_selected_games = st.multiselect(
#     "Escolha os jogos que serão implementados na Claro:", claro_game_choices, default=claro_game_choices
# )

# if st.button("Calcular Projeções para Claro"):
#     try:
#         total_games, total_tickets, avg_games_per_user, avg_ticket_value_per_user, game_percentage = project_client_metrics(
#             game_histories, tickets, claro_clients, claro_weeks, claro_percentage, claro_selected_games
#         )

#         if total_tickets == 0:
#             st.warning("Nenhum ticket foi gerado para os jogos selecionados.")
#         else:
#             st.write("### Resultados das Projeções para a Claro:")
#             st.metric("Partidas Estimadas", f"{total_games:,.0f}".replace(",", "."))
#             st.metric("Tickets Estimados (Valor Total)", f" {total_tickets:,.2f}".replace(",", "."))

#             # CTS - Infraestrutura
#             st.write("### CTS - Infraestrutura")
#             cts_infra = total_games * 0.177
#             st.metric("Custo Estimado de Infraestrutura (CTS)", f"$ {cts_infra:,.2f}".replace(",", "."))


#             st.write("### Percentual de Partidas e Tickets por Jogo:")
#             for game, (pct_games, pct_tickets) in game_percentage.items():
#                 st.write(f"**{game}:** {pct_games:.2f}% partidas, {pct_tickets:.2f}% tickets")

#             st.write("### Explicação do Cálculo:")
#             st.write(f"""
#             - **Total de Partidas Estimadas:**  
#               `{avg_games_per_user:.2f} × {claro_clients} × {claro_percentage / 100:.2f} × {claro_weeks} = {total_games:,.0f}`

#             - **Valor Total de Tickets Estimados:**  
#               `{avg_ticket_value_per_user:.2f} × {claro_clients} × {claro_percentage / 100:.2f} × {claro_weeks} = R$ {total_tickets:,.2f}`
#             """)
#             st.write(f"""
#             - **Cálculo do CTS:**  
#               `{total_games:,.0f} × $ 0,177 = $ {cts_infra:,.2f}`
#             """)
#     except Exception as e:
#         st.error(f"Erro ao calcular projeções para a Claro: {e}")

# from rl.recommend_game import recommend_game

# Recomendação de Jogos com RL
# st.header("Recomendação de Jogos com RL")
# try:
#     # Perfil fictício de jogador (exemplo)
#     player_profile = {
#         "games_played": st.number_input("Jogos Jogados", min_value=0, value=20),
#         "avg_time": st.number_input("Tempo Médio (horas)", min_value=0.0, value=5.5),
#         "tickets_generated": st.number_input("Tickets Gerados", min_value=0, value=300),
#         "engagement": st.slider("Engajamento", min_value=0.5, max_value=1.5, value=1.0, step=0.1),
#     }

#     # Obter recomendação
#     recommended_game = recommend_game(player_profile)

#     st.success(f"Jogo Recomendado: {recommended_game}")
# except Exception as e:
#     st.error(f"Erro na recomendação: {e}")

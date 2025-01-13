import streamlit as st
import json
import plotly.express as px
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
    calculate_event_summary_with_outside_events,
    process_competition_data,
    create_engagement_graph,
    process_age_distribution,
    process_gender_distribution,
)
from src.data_loader import load_json_data

# Personalização do layout
st.set_page_config(
    page_title="Monaco Dashboard",
    page_icon="assets/monaco.png",
    layout="wide",
)

# Adicionar cabeçalho
st.markdown(
    """
    <style>
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #372779;
        padding: 10px;
        border-radius: 10px;
    }
    .header-container h1 {
        color: white;
        font-family: 'Arial', sans-serif;
        margin: 0;
    }
    </style>
    <div class="header-container">
        <h1>Monaco Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    .center-text {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="center-text">Análise e Projeções do GameRoom da Monaco</h1>', unsafe_allow_html=True)
st.markdown('<p class="center-text">Explore os dados de partidas, tickets, usuários e resultados de gamificação.</p>', unsafe_allow_html=True)

# Caminho dos dados
DATA_DIR = "data/"

# Carregando os dados
data = load_json_data(DATA_DIR)

if not data:
    st.error("Erro ao carregar os dados. Verifique os arquivos JSON.")
else:
    # Processar dados
    game_histories = process_json_data(data.get("gamehistories", []), "game_histories")
    tickets = process_json_data(data.get("tickets", []), "tickets")
    users = process_json_data(data.get("users", []), "users")
    game_events = process_json_data(data.get("gameevents", []), "game_events")

    # Crescimento em 2024
    st.header("Crescimento em 2024")
    try:
        games_per_month, total_tickets_amount, users_per_month = analyze_growth(
            game_histories, tickets, users
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Partidas por Mês - 7684")
            st.line_chart(games_per_month)
        with col2:
            st.subheader("Tickets por Mês - 567.593")
            st.line_chart(total_tickets_amount)
        with col3:
            st.subheader("Usuários por Mês - 1314")
            st.line_chart(users_per_month)
    except Exception as e:
        st.error(f"Erro ao analisar crescimento: {e}")

    # Distribuições de Gênero e Idade
    st.header("Distribuições de Gênero e Idade")
    try:
        with open(f"{DATA_DIR}/distribution_data.json") as f:
            distribution_data = json.load(f)
    
        gender_df = process_gender_distribution(distribution_data.get("gender_distribution", {}))
        age_df = process_age_distribution(distribution_data.get("age_distribution", {}))
    
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Gênero")
            gender_fig = px.bar(
                gender_df,
                x="Gênero",
                y="Porcentagem (%)",
                title="Distribuição por Gênero",
                text_auto=True,
            )
            st.plotly_chart(gender_fig, use_container_width=True)
    
        with col2:
            st.subheader("Idade")
            age_fig = px.bar(
                age_df,
                x="Faixa Etária",
                y="Porcentagem (%)",
                title="Distribuição por Idade",
                text_auto=True,
            )
            st.plotly_chart(age_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao processar distribuições: {e}")

    # Distribuição de Tickets
    st.header("Distribuição de Tickets")
    try:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Por Jogos")
            game_ticket_distribution = calculate_game_distribution(tickets)
            st.bar_chart(game_ticket_distribution)

        with col2:
            st.subheader("Por Meses")
            tickets_by_game_and_month = calculate_tickets_by_game_and_month(tickets)
            st.line_chart(tickets_by_game_and_month)
    except Exception as e:
        st.error(f"Erro ao calcular distribuição de tickets: {e}")

    # Resumo de Tabelas
    st.header("Resumo de Eventos")
    try:
        col1, col2, col3 = st.columns(3)
        with col1:
            event_summary_df = calculate_event_summary_with_outside_events(
                game_histories, tickets, game_events
            )
            st.subheader("Tickets e Partidas por Evento")
            st.dataframe(event_summary_df)

        with col2:
            orders_summary_df = calculate_orders_by_event(
                process_json_data(data.get("orders", []), "orders"), game_events
            )
            st.subheader("Orders por Evento")
            st.dataframe(orders_summary_df)

        with col3:
            unique_order_values_summary_df = calculate_unique_order_values_by_event(
                process_json_data(data.get("orders", []), "orders"), game_events
            )
            st.subheader("Valores e Compras por Evento")
            st.dataframe(unique_order_values_summary_df)
    except Exception as e:
        st.error(f"Erro ao calcular tabelas de resumo: {e}")

    # Heavy Users
    # Seção: Heavy Users da Monaco
st.header("Top Heavy Users")

try:
    # Dividir em duas colunas para melhor organização
    col1, col2 = st.columns([1, 1])  # Definir proporções iguais para as colunas

    with col1:
        st.subheader("Top 30 Heavy Users")
        top_heavy_users_df = calculate_top_heavy_users(game_histories, users)
        st.dataframe(top_heavy_users_df.style.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#372779'), ('color', 'white')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
            {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', 'white')]}
        ]), height=400)

    with col2:
        natal_event_name = "Campeonato Season 6 - Natal"
        st.subheader(f"Top 10 Heavy Users - {natal_event_name}")
        top_users_natal_df = calculate_top_users_event_summary(
            game_histories, users, natal_event_name, "2024-12-13", "2024-12-24", top_n=10
        )
        st.dataframe(top_users_natal_df.style.set_table_styles([
            {'selector': 'thead th', 'props': [('background-color', '#372779'), ('color', 'white')]},
            {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
            {'selector': 'tbody tr:nth-child(odd)', 'props': [('background-color', 'white')]}
        ]), height=400)

except Exception as e:
    st.error(f"Erro ao processar usuários: {e}")

        # Carregar JSON de competições
try:
    with open("data/competitions_gameroom.json") as f:
        competitions_data = json.load(f)["competitions"]
except FileNotFoundError:
    st.error("Arquivo 'competitions_gameroom.json' não encontrado no diretório 'data/'.")
    st.stop()
except KeyError:
    st.error("A chave 'competitions' está ausente no JSON.")
    st.stop()

# Título do Dashboard
st.title("Análises de Engajamento por Competição")

# Obter nomes das competições
competition_names = [comp["competition"] for comp in competitions_data]

# Adicionar seletor de competição com uma chave única
selected_competition = st.selectbox(
    "Selecione uma competição:", competition_names, key="competition_selectbox"
)

# Filtrar dados da competição selecionada
selected_data = next(comp for comp in competitions_data if comp["competition"] == selected_competition)

# Processar dados da competição
competition_df = process_competition_data(selected_data)

# Obter o valor de total_average_period
total_average_period = selected_data["engagement_data"]["total_period"].get("total_average_period", "N/A")

# Criar gráfico de engajamento
engagement_graph = create_engagement_graph(competition_df, selected_competition)

# Exibir cabeçalho, gráfico e total_average_period
# st.header(f"Average Time - {selected_competition}")
st.metric("Average Period (Total)", total_average_period)  # Exibe o valor como métrica
st.plotly_chart(engagement_graph, key=f"plotly_chart_{selected_competition}")

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

# Adicionar rodapé
st.markdown(
    """
    <style>
    .footer-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        border-radius: 10px;
        width: 100%;
        margin-top: 20px;
    }
    .footer-container p {
        color: black;
        font-family: 'Arial', sans-serif;
        margin: 0;
        font-size: 0.9rem;
    }
    .footer-container a {
        color: #00acee;
        text-decoration: none;
        font-weight: bold;
        margin-left: 5px;
        margin-right: 5px;
    }
    .footer-container a:hover {
        text-decoration: underline;
    }
    </style>
    <div class="footer-container">
        <p>© 2025 Monaco Soluções LTDA. Todos os direitos reservados. | Al Rio Negro 503, Sala 2020, Alphaville/SP - BR</p>
        <p>
            <a href="https://www.linkedin.com/company/monaco-gg" target="_blank">LinkedIn</a> |
            <a href="https://www.monaco.gg" target="_blank">Site</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

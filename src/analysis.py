import pandas as pd
import plotly.express as px
import streamlit as st

def plot_game_distribution(ticket_distribution):
    fig = px.bar(ticket_distribution, x=ticket_distribution.index, y="amount", title="Distribuição de Tickets")
    fig.update_layout(xaxis_title="Jogos", yaxis_title="Quantidade de Tickets")
    st.plotly_chart(fig)

def process_json_data(data, data_type):
    df = pd.DataFrame(data)
    if "createdAt" in df.columns:
        df["createdAt"] = df["createdAt"].apply(
            lambda x: pd.to_datetime(x["$date"]["$numberLong"], unit="ms") if isinstance(x, dict) else pd.to_datetime(x, unit="ms")
        )
    if "amount" in df.columns and data_type == "tickets":
        df["amount"] = df["amount"].apply(lambda x: int(x["$numberInt"]) if isinstance(x, dict) else x)
    if "_id" in df.columns:
        df["_id"] = df["_id"].apply(lambda x: x.get("$oid") if isinstance(x, dict) else x)
    if "user" in df.columns and data_type == "tickets":
        df["user"] = df["user"].apply(lambda x: x.get("$oid") if isinstance(x, dict) else x)
    return df

# Análise Crescimento Partidas, Tickets e Usuários
def analyze_growth(game_histories, tickets, users):
    game_histories["month"] = game_histories["createdAt"].dt.to_period("M")
    tickets["month"] = tickets["createdAt"].dt.to_period("M")
    users["month"] = users["createdAt"].dt.to_period("M")

    games_per_month = game_histories["month"].value_counts().sort_index()
    total_tickets_amount = tickets.groupby("month")["amount"].sum().sort_index()
    users_per_month = users["month"].value_counts().sort_index()

    games_per_month.index = games_per_month.index.astype(str)
    total_tickets_amount.index = total_tickets_amount.index.astype(str)
    users_per_month.index = users_per_month.index.astype(str)

    return games_per_month, total_tickets_amount, users_per_month

# Distribuição Tickets por Jogos
def calculate_game_distribution(tickets):
    ticket_distribution = tickets.groupby("gameId")["amount"].sum()
    ticket_distribution.index = ticket_distribution.index.map({
        "1": "The Runner",
        "2": "Day One",
        "3": "Lava Rush",
        "4": "Super Monaco"
    })
    return ticket_distribution

def calculate_tickets_by_game_and_month(tickets):
    tickets["month"] = tickets["createdAt"].dt.to_period("M")
    tickets_by_game_and_month = tickets.groupby(["month", "gameId"])["amount"].sum().unstack(fill_value=0)
    tickets_by_game_and_month.columns = tickets_by_game_and_month.columns.map({
        "1": "The Runner",
        "2": "Day One",
        "3": "Lava Rush",
        "4": "Super Monaco"
    })
    tickets_by_game_and_month.index = tickets_by_game_and_month.index.astype(str)
    return tickets_by_game_and_month

# Cálculo de tickets por nível
def calculate_tickets_by_level(total_tickets):
    level_distribution = {
        "Easy": 0.25,
        "Medium": 0.35,
        "Hard": 0.30,
        "Extreme": 0.10,
    }
    tickets_by_level = {level: total_tickets * pct for level, pct in level_distribution.items()}
    return tickets_by_level

def project_client_metrics(game_histories, tickets, num_clients, weeks, base_percentage, selected_games):
    adjusted_clients = num_clients * (base_percentage / 100)
    selected_game_ids = {
        "The Runner": "1",
        "Day One": "2",
        "Lava Rush": "3",
        "Super Monaco": "4",
    }
    selected_game_ids = [selected_game_ids[game] for game in selected_games]

    filtered_games = game_histories[game_histories["gameId"].isin(selected_game_ids)]
    filtered_tickets = tickets[tickets["gameId"].isin(selected_game_ids)]

    if filtered_games.empty or filtered_tickets.empty:
        return 0, 0, 0, 0, {}

    avg_games_per_user = filtered_games.shape[0] / filtered_games["userId"].nunique() if filtered_games["userId"].nunique() > 0 else 0
    avg_ticket_value_per_user = filtered_tickets["amount"].sum() / filtered_tickets["user"].nunique() if filtered_tickets["user"].nunique() > 0 else 0

    total_games = avg_games_per_user * adjusted_clients * weeks
    total_tickets = avg_ticket_value_per_user * adjusted_clients * weeks

    game_percentage = {}
    for game in selected_games:
        game_id = selected_game_ids[selected_games.index(game)]
        game_games = filtered_games[filtered_games["gameId"] == game_id].shape[0]
        game_tickets = filtered_tickets[filtered_tickets["gameId"] == game_id]["amount"].sum()

        game_percentage[game] = (
            (game_games / filtered_games.shape[0]) * 100 if filtered_games.shape[0] > 0 else 0,
            (game_tickets / filtered_tickets["amount"].sum()) * 100 if filtered_tickets["amount"].sum() > 0 else 0,
        )

    return total_games, total_tickets, avg_games_per_user, avg_ticket_value_per_user, game_percentage

# Distribuição Tickets por Jogos fora de Eventos(Campeonatos)
def calculate_event_summary_with_outside_events(game_histories, tickets, game_events):
    game_events["startDate"] = game_events["startDate"].apply(
        lambda x: pd.to_datetime(x["$date"]["$numberLong"], unit="ms") if isinstance(x, dict) else pd.to_datetime(x, unit="ms")
    )
    game_events["endDate"] = game_events["endDate"].apply(
        lambda x: pd.to_datetime(x["$date"]["$numberLong"], unit="ms") if isinstance(x, dict) else pd.to_datetime(x, unit="ms")
    )

    event_summary = []

    for _, event in game_events.iterrows():
        event_name = event["title"]
        start_date = event["startDate"]
        end_date = event["endDate"]

        filtered_games = game_histories[
            (game_histories["createdAt"] >= start_date) & (game_histories["createdAt"] <= end_date)
        ]
        filtered_tickets = tickets[
            (tickets["createdAt"] >= start_date) & (tickets["createdAt"] <= end_date)
        ]

        total_games = filtered_games.shape[0]
        total_tickets = filtered_tickets["amount"].sum()
        event_duration_days = (end_date - start_date).days + 1  # Adiciona 1 para incluir o último dia
        avg_games_per_day = total_games / event_duration_days if event_duration_days > 0 else 0

        event_summary.append({
            "Evento": event_name,
            "Total de Partidas": total_games,
            "Total de Tickets": total_tickets,
            "Média de Partidas por Dia": round(avg_games_per_day, 2),
            "Início": start_date.strftime("%Y-%m-%d"),
            "Fim": end_date.strftime("%Y-%m-%d"),
        })

    for i in range(len(game_events) - 1):
        interval_start = game_events.iloc[i]["endDate"] + pd.Timedelta(days=1)
        interval_end = game_events.iloc[i + 1]["startDate"] - pd.Timedelta(days=1)

        filtered_games = game_histories[
            (game_histories["createdAt"] >= interval_start) & (game_histories["createdAt"] <= interval_end)
        ]
        filtered_tickets = tickets[
            (tickets["createdAt"] >= interval_start) & (tickets["createdAt"] <= interval_end)
        ]

        total_games = filtered_games.shape[0]
        total_tickets = filtered_tickets["amount"].sum()
        interval_duration_days = (interval_end - interval_start).days + 1  # Adiciona 1 para incluir o último dia
        avg_games_per_day = total_games / interval_duration_days if interval_duration_days > 0 else 0

        event_summary.append({
            "Evento": f"Intervalo {i + 1}",
            "Total de Partidas": total_games,
            "Total de Tickets": total_tickets,
            "Média de Partidas por Dia": round(avg_games_per_day, 2),
            "Início": interval_start.strftime("%Y-%m-%d"),
            "Fim": interval_end.strftime("%Y-%m-%d"),
        })

    # Agrupar intervalos em uma única linha
    interval_games = sum(item["Total de Partidas"] for item in event_summary if "Intervalo" in item["Evento"])
    interval_tickets = sum(item["Total de Tickets"] for item in event_summary if "Intervalo" in item["Evento"])
    total_interval_days = sum(
        (pd.to_datetime(item["Fim"]) - pd.to_datetime(item["Início"])).days + 1
        for item in event_summary if "Intervalo" in item["Evento"]
    )
    avg_interval_games_per_day = interval_games / total_interval_days if total_interval_days > 0 else 0

    if interval_games > 0 or interval_tickets > 0:
        event_summary.append({
            "Evento": "Intervalos Agrupados",
            "Total de Partidas": interval_games,
            "Total de Tickets": interval_tickets,
            "Média de Partidas por Dia": round(avg_interval_games_per_day, 2),
            "Início": game_events["endDate"].min().strftime("%Y-%m-%d"),
            "Fim": game_events["endDate"].max().strftime("%Y-%m-%d"),
        })

    return pd.DataFrame(event_summary)

# Distribuição de Orders(Pagamentos) por Eventos(Campeonatos)
def calculate_orders_by_event(orders, game_events):
    """
    Calcula o resumo de Orders (pagamentos concluídos) por evento, incluindo intervalos fora dos eventos.

    :param orders: DataFrame de Orders.
    :param game_events: DataFrame de eventos de jogos.
    :return: DataFrame com o resumo de Orders por evento.
    """
    # Processar datas de início e fim dos eventos
    game_events["startDate"] = game_events["startDate"].apply(
        lambda x: pd.to_datetime(x["$date"]["$numberLong"], unit="ms") if isinstance(x, dict) else pd.to_datetime(x, unit="ms")
    )
    game_events["endDate"] = game_events["endDate"].apply(
        lambda x: pd.to_datetime(x["$date"]["$numberLong"], unit="ms") if isinstance(x, dict) else pd.to_datetime(x, unit="ms")
    )

    # Processar o campo totalAmount para garantir que esteja numérico
    if "totalAmount" in orders.columns:
        orders["totalAmount"] = orders["totalAmount"].apply(
            lambda x: float(x["$numberDouble"]) if isinstance(x, dict) and "$numberDouble" in x else float(x) if isinstance(x, (int, float)) else 0.0
        )

    # Filtrar apenas Orders com pagamento "paid"
    orders = orders[orders["paymentStatus"] == "paid"]

    event_summary = []

    # Calcular Orders dentro de cada evento
    for _, event in game_events.iterrows():
        event_name = event["title"]
        start_date = event["startDate"]
        end_date = event["endDate"]

        filtered_orders = orders[
            (orders["createdAt"] >= start_date) & (orders["createdAt"] <= end_date)
        ]

        total_orders = filtered_orders.shape[0]
        total_amount = filtered_orders["totalAmount"].sum()

        event_summary.append({
            "Evento": event_name,
            "Total de Orders": total_orders,
            "Valor Total (R$)": round(total_amount, 2),
            "Início": start_date.strftime("%Y-%m-%d"),
            "Fim": end_date.strftime("%Y-%m-%d")
        })

    # Calcular Orders fora dos eventos
    for i in range(len(game_events) - 1):
        interval_start = game_events.iloc[i]["endDate"] + pd.Timedelta(days=1)
        interval_end = game_events.iloc[i + 1]["startDate"] - pd.Timedelta(days=1)

        filtered_orders = orders[
            (orders["createdAt"] >= interval_start) & (orders["createdAt"] <= interval_end)
        ]

        total_orders = filtered_orders.shape[0]
        total_amount = filtered_orders["totalAmount"].sum()

        event_summary.append({
            "Evento": f"Intervalo {i + 1}",
            "Total de Orders": total_orders,
            "Valor Total (R$)": round(total_amount, 2),
            "Início": interval_start.strftime("%Y-%m-%d"),
            "Fim": interval_end.strftime("%Y-%m-%d")
        })

    # Agrupar intervalos em uma única linha
    interval_orders = sum(item["Total de Orders"] for item in event_summary if "Intervalo" in item["Evento"])
    interval_amount = sum(item["Valor Total (R$)"] for item in event_summary if "Intervalo" in item["Evento"])
    if interval_orders > 0 or interval_amount > 0:
        event_summary.append({
            "Evento": "Intervalos Agrupados",
            "Total de Orders": interval_orders,
            "Valor Total (R$)": round(interval_amount, 2),
            "Início": game_events["endDate"].min().strftime("%Y-%m-%d"),
            "Fim": game_events["endDate"].max().strftime("%Y-%m-%d")
        })

    return pd.DataFrame(event_summary)

# Cálculo de compras únicas(valores) por eventos
def calculate_unique_order_values_by_event(orders, game_events):
    """
    Calcula os valores únicos de compras (totalAmount) e a quantidade de compras feitas por evento.

    :param orders: DataFrame de Orders.
    :param game_events: DataFrame de eventos de jogos.
    :return: DataFrame com resumo de valores únicos e quantidades por evento.
    """
    game_events["startDate"] = game_events["startDate"].apply(
        lambda x: pd.to_datetime(x["$date"]["$numberLong"], unit="ms") if isinstance(x, dict) else pd.to_datetime(x)
    )
    game_events["endDate"] = game_events["endDate"].apply(
        lambda x: pd.to_datetime(x["$date"]["$numberLong"], unit="ms") if isinstance(x, dict) else pd.to_datetime(x)
    )

    # Garantir que o campo totalAmount está em formato numérico
    orders["totalAmount"] = orders["totalAmount"].apply(
        lambda x: float(x["$numberDouble"]) if isinstance(x, dict) and "$numberDouble" in x else float(x) if isinstance(x, (int, float)) else 0.0
    )

    summary = []

    for _, event in game_events.iterrows():
        event_name = event["title"]
        start_date = event["startDate"]
        end_date = event["endDate"]

        # Filtrar Orders dentro do período do evento
        event_orders = orders[
            (orders["createdAt"] >= start_date) &
            (orders["createdAt"] <= end_date) &
            (orders["paymentStatus"] == "paid")
        ]

        # Agrupar valores únicos e suas quantidades
        total_amount_counts = event_orders["totalAmount"].value_counts().reset_index()
        total_amount_counts.columns = ["Valor Único (R$)", "Quantidade"]
        total_amount_counts["Evento"] = event_name

        summary.append(total_amount_counts)

    # Concatenar resultados de todos os eventos
    result = pd.concat(summary, ignore_index=True)

    return result

# Lista 30 Heavy Users da Monaco
def calculate_top_heavy_users(game_histories, users, top_n=30):
    """
    Calcula os usuários com maior número de partidas.

    :param game_histories: DataFrame com histórico de jogos.
    :param users: DataFrame com dados dos usuários.
    :param top_n: Número de usuários a serem exibidos (padrão: 30).
    :return: DataFrame com os top N heavy users e suas respectivas quantidades de partidas.
    """
    # Contar partidas por usuário
    user_game_counts = game_histories["userId"].value_counts().reset_index()
    user_game_counts.columns = ["userId", "Total de Partidas"]

    # Processar campo _id no DataFrame de usuários
    if "_id" in users.columns:
        users["_id"] = users["_id"].apply(lambda x: x.get("$oid") if isinstance(x, dict) else x)

    # Mesclar com informações dos usuários
    user_game_counts = user_game_counts.merge(users, left_on="userId", right_on="_id", how="left")

    # Selecionar colunas relevantes
    user_game_counts = user_game_counts[["Total de Partidas", "nickname"]]

    # Ordenar e selecionar os top N usuários
    top_users = user_game_counts.sort_values(by="Total de Partidas", ascending=False).head(top_n)

    # Preencher valores ausentes com "Desconhecido"
    top_users.fillna("Desconhecido", inplace=True)

    return top_users

def calculate_top_users_event_summary(game_histories, users, event_name, start_date, end_date, top_n=10):
    """
    Calcula os top usuários com mais partidas durante um evento específico.

    :param game_histories: DataFrame com histórico de partidas.
    :param users: DataFrame com dados dos usuários.
    :param event_name: Nome do evento.
    :param start_date: Data de início do evento.
    :param end_date: Data de término do evento.
    :param top_n: Número de usuários a exibir (padrão: 10).
    :return: DataFrame com resumo de partidas por dia e jogo para os top usuários.
    """
    # Filtrar partidas dentro do intervalo do evento
    filtered_games = game_histories[
        (game_histories["createdAt"] >= pd.to_datetime(start_date)) &
        (game_histories["createdAt"] <= pd.to_datetime(end_date))
    ]

    # Adicionar a coluna 'date' ao DataFrame de partidas
    filtered_games["date"] = filtered_games["createdAt"].dt.date

    # Contar partidas por usuário, jogo e data
    user_game_counts = filtered_games.groupby(["userId", "gameId", "date"]).size().reset_index(name="Partidas Por Dia")

    # Mapear gameId para nomes legíveis
    user_game_counts["gameId"] = user_game_counts["gameId"].map({
        "1": "The Runner",
        "2": "Day One",
        "3": "Lava Rush",
        "4": "Super Monaco"
    })

    # Contar total de partidas por usuário
    total_user_games = filtered_games.groupby("userId").size().reset_index(name="Total Partidas")

    # Mesclar com informações dos usuários
    if "_id" in users.columns:
        users["_id"] = users["_id"].apply(lambda x: x.get("$oid") if isinstance(x, dict) else x)

    user_game_counts = user_game_counts.merge(users, left_on="userId", right_on="_id", how="left")

    # Selecionar os top N usuários com base no total de partidas
    top_users = total_user_games.nlargest(top_n, "Total Partidas")["userId"]
    top_users_summary = user_game_counts[user_game_counts["userId"].isin(top_users)]

    return top_users_summary[["nickname", "gameId", "date", "Partidas Por Dia"]]

def process_competition_data(competition):
    """
    Processa os dados de uma competição para análise.
    """
    daily_data = []
    for daily in competition["engagement_data"]["daily"]:
        daily_data.append({
            "date": pd.to_datetime(daily["date"]),
            "total_average_time": daily["total_average_time"],
            "observations": daily.get("observations", ""),
        })

    df = pd.DataFrame(daily_data)

    # Converter total_average_time para segundos
    df["total_average_time_segundos"] = df["total_average_time"].apply(
        lambda x: sum(int(part) * 60 ** i for i, part in enumerate(reversed(x.split(":"))))
    )
    return df

def create_engagement_graph(dataframe, competition_name):
    """
    Gera um gráfico de linha para engajamento diário.
    """
    fig = px.line(
        dataframe,
        x="date",
        y="total_average_time_segundos",
        title=f"Evolução do Engajamento Diário - {competition_name}",
        labels={
            "date": "Data",
            "total_average_time_segundos": "Tempo Médio de Tela (segundos)"
        },
        markers=True
    )
    # Adicionar anotações para observações
    for _, row in dataframe.iterrows():
        if row["observations"]:
            fig.add_annotation(
                x=row["date"],
                y=row["total_average_time_segundos"],
                text=row["observations"],
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-30
            )
    return fig

# Distribuição de Gênero e Idade
def process_gender_distribution(gender_distribution):
    """
    Processa a distribuição de gênero em um DataFrame.
    """
    return pd.DataFrame({
        "Gênero": gender_distribution.keys(),
        "Porcentagem (%)": gender_distribution.values()
    })

def process_age_distribution(age_distribution):
    """
    Processa a distribuição de idade em um DataFrame.
    """
    return pd.DataFrame({
        "Faixa Etária": age_distribution.keys(),
        "Porcentagem (%)": [float(value.strip('%')) for value in age_distribution.values()]
    })
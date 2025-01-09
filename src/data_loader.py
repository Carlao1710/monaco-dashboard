import json
import os

def load_json_data(data_dir):
    """
    Carrega arquivos JSON de um diretório e os converte em dicionários de DataFrames.
    """
    data = {}
    try:
        for file_name in os.listdir(data_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(data_dir, file_name)
                with open(file_path, "r") as f:
                    data[file_name.replace(".json", "")] = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
    return data
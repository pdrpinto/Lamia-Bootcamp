import airflow
import requests
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

# Definição de argumentos padrão da DAG
default_args = {
    'owner': 'Airflow',  # Define o proprietário da DAG
    'start_date': airflow.utils.dates.days_ago(2),  # Define a data de início da DAG
}

# Dicionário contendo APIs de geolocalização e seus respectivos endpoints
IP_GEOLOCATION_APIS = {
    'ip-api': 'http://ip-api.com/json/',
    'ipstack': 'https://api.ipstack.com/',
    'ipinfo': 'https://ipinfo.io/json'
}

# Função para verificar quais APIs retornam um país válido
def check_api():
    apis = []  # Lista para armazenar as APIs que retornaram um país válido
    for api, link in IP_GEOLOCATION_APIS.items():
        r = requests.get(link)  # Faz uma requisição HTTP à API
        try:
            data = r.json()  # Tenta converter a resposta para JSON
            if data and 'country' in data and len(data['country']):  # Verifica se o campo 'country' existe e não está vazio
                apis.append(api)  # Adiciona a API à lista
        except ValueError:
            pass  # Se houver erro na conversão JSON, apenas ignora
    return apis if len(apis) > 0 else 'none'  # Retorna as APIs válidas ou 'none' caso nenhuma funcione

# Definição da DAG
with DAG(dag_id='branch_dag', 
         default_args=default_args, 
         schedule_interval="@once"  # A DAG será executada apenas uma vez
    ) as dag:

    # BranchPythonOperator
    # A próxima tarefa será determinada pelo retorno da função check_api
    check_api = BranchPythonOperator(
        task_id='check_api',
        python_callable=check_api  # Define a função Python que será executada
    )

    # Tarefa dummy que será executada caso nenhuma API retorne dados válidos
    none = DummyOperator(
        task_id='none'
    )

    # Tarefa dummy para representar a etapa final, sendo executada se ao menos uma API for válida
    save = DummyOperator(task_id='save', trigger_rule='one_success')

    # Definição da dependência: se nenhuma API for válida, a DAG segue pelo caminho do operador 'none'
    check_api >> none >> save

    # Criando dinamicamente tarefas para cada API no dicionário
    for api in IP_GEOLOCATION_APIS:
        process = DummyOperator(
            task_id=api  # Cria um operador dummy para cada API
        )
    
        # Define que cada API validada será processada antes de seguir para a tarefa final 'save'
        check_api >> process >> save

import airflow
import requests
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator

# Definição dos argumentos padrão
default_args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(1),
}

# URL a ser testada
TEST_URL = "https://www.google.com"

# Função que verifica se a URL está acessível
def check_connection():
    try:
        response = requests.get(TEST_URL, timeout=5)  # Faz uma requisição GET com timeout de 5s
        if response.status_code == 200:
            return 'proceed'  # Se o site estiver acessível, continua a DAG
    except requests.RequestException:
        pass
    return 'abort'  # Caso contrário, interrompe a DAG

# Definição da DAG
with DAG(dag_id='check_connection_dag',
         default_args=default_args,
         schedule_interval="@once") as dag:

    # Tarefa que verifica se o site está acessível
    check_connection_task = BranchPythonOperator(
        task_id='check_connection',
        python_callable=check_connection
    )

    # Tarefa para quando a conexão for bem-sucedida
    proceed = DummyOperator(task_id='proceed')

    # Tarefa para quando a conexão falhar
    abort = DummyOperator(task_id='abort')

    # Definição das dependências
    check_connection_task >> [proceed, abort]

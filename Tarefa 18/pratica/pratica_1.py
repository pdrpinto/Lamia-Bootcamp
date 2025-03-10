import airflow
import random
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

# Definição dos argumentos padrão da DAG
default_args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(1),
}

# Lista com os possíveis caminhos
API_OPTIONS = ['time_api_1', 'time_api_2']

# Função que escolhe aleatoriamente qual API será usada
def choose_api():
    return random.choice(API_OPTIONS)

# Definição da DAG
with DAG(dag_id='random_api_dag',
         default_args=default_args,
         schedule_interval="@once") as dag:

    # Tarefa de decisão que escolhe aleatoriamente qual API usar
    choose_api_task = BranchPythonOperator(
        task_id='choose_api',
        python_callable=choose_api
    )

    # Tarefas dummy para representar chamadas a APIs diferentes
    time_api_1 = DummyOperator(task_id='time_api_1')
    time_api_2 = DummyOperator(task_id='time_api_2')

    # Tarefa final, que será executada independentemente da API escolhida
    save_data = DummyOperator(task_id='save_data', trigger_rule='one_success')

    # Configuração das dependências
    choose_api_task >> [time_api_1, time_api_2] >> save_data

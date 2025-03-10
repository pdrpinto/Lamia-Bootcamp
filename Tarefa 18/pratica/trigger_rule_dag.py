import airflow
import requests
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

# Configuração de argumentos padrão para a DAG
default_args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(1),  # Define a data de início da DAG como um dia atrás
}

# Funções que simulam o download de sites e notificações
def download_website_a():
    print("download_website_a")
    #raise ValueError("error")  # Simula erro (comportamento comentado)

def download_website_b():
    print("download_website_b")

def download_failed():
    print("download_failed")

def download_succeed():
    print("download_succeed")

def process():
    print("process")

def notif_a():
    print("notif_a")

def notif_b():
    print("notif_b")

# Definição da DAG
with DAG(dag_id='trigger_rule_dag', 
    default_args=default_args, 
    schedule_interval="@daily") as dag:

    # Regras de disparo (trigger rules) disponíveis:
    # - all_success: só executa se todas as tarefas anteriores forem bem-sucedidas
    # - all_failed: só executa se todas as tarefas anteriores falharem
    # - all_done: executa independentemente do sucesso ou falha das tarefas anteriores
    # - one_failed: executa se pelo menos uma tarefa anterior falhar
    # - one_success: executa se pelo menos uma tarefa anterior tiver sucesso
    # - none_failed: executa se nenhuma tarefa anterior falhar
    # - none_skipped: executa se nenhuma tarefa anterior for ignorada
    
    # Tarefa para baixar o website A
    download_website_a_task = PythonOperator(
        task_id='download_website_a',
        python_callable=download_website_a,
        trigger_rule="all_success"  # Executa apenas se todas as tarefas anteriores forem bem-sucedidas
    )

    # Tarefa para baixar o website B
    download_website_b_task = PythonOperator(
        task_id='download_website_b',
        python_callable=download_website_b,
        trigger_rule="all_success"
    )

    # Tarefa que é acionada se todas as tentativas de download falharem
    download_failed_task = PythonOperator(
        task_id='download_failed',
        python_callable=download_failed,
        trigger_rule="all_failed"
    )

    # Tarefa que é acionada se todas as tentativas de download forem bem-sucedidas
    download_succeed_task = PythonOperator(
        task_id='download_succeed',
        python_callable=download_succeed,
        trigger_rule="all_success"
    )

    # Tarefa de processamento, executada se pelo menos um download for bem-sucedido
    process_task = PythonOperator(
        task_id='process',
        python_callable=process,
        trigger_rule="one_success"
    )

    # Notificação A, executada se nenhuma tarefa anterior falhar
    notif_a_task = PythonOperator(
        task_id='notif_a',
        python_callable=notif_a,
        trigger_rule="none_failed"
    )

    # Notificação B, executada se pelo menos uma tarefa anterior falhar
    notif_b_task = PythonOperator(
        task_id='notif_b',
        python_callable=notif_b,
        trigger_rule="one_failed"
    )

    # Definição das dependências entre as tarefas:
    # - Se o download falhar ou tiver sucesso, a tarefa de processamento será acionada
    [download_failed_task, download_succeed_task] >> process_task

    # - As tarefas de download determinam o sucesso ou falha do download
    [download_website_a_task, download_website_b_task] >> download_failed_task
    [download_website_a_task, download_website_b_task] >> download_succeed_task

    # - A tarefa de processamento aciona as notificações, dependendo do resultado
    process_task >> [notif_a_task, notif_b_task]

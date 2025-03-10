from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

# Definição de argumentos padrão para a DAG
default_args = {
    'start_date': datetime(2019, 1, 1),  # Define a data de início da DAG
    'owner': 'Airflow',  # Define o proprietário da DAG
    'email': 'owner@test.com'  # E-mail para notificações (não está configurado para alertas de erro)
}

# Definição da DAG
with DAG(dag_id='queue_dag', 
         schedule_interval='0 0 * * *',  # Agendada para rodar diariamente à meia-noite
         default_args=default_args, 
         catchup=False  # Desativa a execução retroativa de execuções perdidas
    ) as dag:
    
    # Tarefas que exigem um worker com SSD para operações de alta demanda de I/O
    t_1_ssd = BashOperator(
        task_id='t_1_ssd',
        bash_command='echo "I/O intensive task"',
        queue='worker_ssd'  # Especifica a fila (worker) onde a tarefa será executada
    )

    t_2_ssd = BashOperator(
        task_id='t_2_ssd',
        bash_command='echo "I/O intensive task"',
        queue='worker_ssd'
    )

    t_3_ssd = BashOperator(
        task_id='t_3_ssd',
        bash_command='echo "I/O intensive task"',
        queue='worker_ssd'
    )

    # Tarefas que exigem um worker otimizado para CPU
    t_4_cpu = BashOperator(
        task_id='t_4_cpu',
        bash_command='echo "CPU intensive task"',
        queue='worker_cpu'
    )

    t_5_cpu = BashOperator(
        task_id='t_5_cpu',
        bash_command='echo "CPU intensive task"',
        queue='worker_cpu'
    )

    # Tarefa que depende do Apache Spark para execução
    t_6_spark = BashOperator(
        task_id='t_6_spark',
        bash_command='echo "Spark dependency task"',
        queue='worker_spark'
    )

    # Tarefa Dummy apenas para sincronizar a execução das tarefas anteriores
    task_7 = DummyOperator(task_id='task_7')

    # Definição das dependências: todas as tarefas anteriores devem ser concluídas antes de `task_7`
    [t_1_ssd, t_2_ssd, t_3_ssd, t_4_cpu, t_5_cpu, t_6_spark] >> task_7

from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

# Definição de argumentos padrão da DAG
default_args = {
    'start_date': datetime(2019, 1, 1),  # Define a data de início da DAG
    'owner': 'Airflow',  # Define o proprietário da DAG
    'email': 'owner@test.com'  # E-mail para notificações (não está configurado para alertas de erro)
}

# Definição da DAG
with DAG(dag_id='pool_dag', 
         schedule_interval='0 0 * * *',  # Executa diariamente à meia-noite
         default_args=default_args, 
         catchup=False  # Evita execução retroativa de execuções perdidas
    ) as dag:
    
    # Obtém a taxa de câmbio com base no EUR e armazena em XCOM
    get_forex_rate_EUR = SimpleHttpOperator(
        task_id='get_forex_rate_EUR',
        method='GET',
        priority_weight=1,  # Define a prioridade da execução dentro do pool
        pool='forex_api_pool',  # Usa o pool 'forex_api_pool' para limitar concorrência
        http_conn_id='forex_api',  # Conexão HTTP configurada no Airflow
        endpoint='/latest?base=EUR',  # Endpoint da API para obter taxas de câmbio
        xcom_push=True  # Armazena o resultado na variável XCOM
    )
 
    # Obtém a taxa de câmbio com base no USD e armazena em XCOM
    get_forex_rate_USD = SimpleHttpOperator(
        task_id='get_forex_rate_USD',
        method='GET',
        priority_weight=2,  # Tem maior prioridade que a tarefa anterior
        pool='forex_api_pool',  
        http_conn_id='forex_api',
        endpoint='/latest?base=USD',
        xcom_push=True
    )
 
    # Obtém a taxa de câmbio com base no JPY e armazena em XCOM
    get_forex_rate_JPY = SimpleHttpOperator(
        task_id='get_forex_rate_JPY',
        method='GET',
        priority_weight=3,  # Tem a maior prioridade
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint='/latest?base=JPY',
        xcom_push=True
    )
 
    # Comando Bash que exibe os IDs das tarefas e seus valores armazenados no XCOM
    bash_command="""
        {% for task in dag.task_ids %}
            echo "{{ task }}"  # Exibe o nome da tarefa
            echo "{{ ti.xcom_pull(task) }}"  # Obtém o resultado da XCOM para essa tarefa
        {% endfor %}
    """

    # Exibe os dados obtidos das chamadas HTTP anteriores
    show_data = BashOperator(
        task_id='show_result',
        bash_command=bash_command
    )

    # Define as dependências: todas as requisições de taxa de câmbio devem ser concluídas antes da exibição dos resultados
    [get_forex_rate_EUR, get_forex_rate_USD, get_forex_rate_JPY] >> show_data

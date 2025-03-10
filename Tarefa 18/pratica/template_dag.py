import sys
import airflow
from airflow import DAG, macros
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime, timedelta

# Adiciona o diretório onde estão os scripts Python ao caminho de busca do Python
sys.path.insert(1, '/usr/local/airflow/dags/scripts')

# Importa a função que processa os logs, localizada em um script externo
from process_logs import process_logs_func

# Diretório de logs usando templating do Airflow para definir o caminho dinamicamente
TEMPLATED_LOG_DIR = """{{ var.value.source_path }}/data/{{ macros.ds_format(ts_nodash, "%Y%m%dT%H%M%S", "%Y-%m-%d-%H-%M") }}/"""

# Definição dos argumentos padrão da DAG
default_args = {
    "owner": "Airflow",
    "start_date": airflow.utils.dates.days_ago(1),  # DAG começa a rodar a partir de um dia atrás
    "depends_on_past": False,  # Execuções não dependem de execuções passadas
    "email_on_failure": False,  # Desativa notificações por e-mail em caso de falha
    "email_on_retry": False,  # Desativa notificações por e-mail em caso de tentativa de reexecução
    "email": "youremail@host.com",  # E-mail para notificações (não utilizado)
    "retries": 1  # Número de tentativas em caso de falha
}

# Definição da DAG
with DAG(dag_id="template_dag", schedule_interval="@daily", default_args=default_args) as dag:

    # Tarefa t0: Executa um comando Bash para exibir o timestamp formatado
    t0 = BashOperator(
        task_id="t0",
        bash_command="echo {{ ts_nodash }} - {{ macros.ds_format(ts_nodash, '%Y%m%dT%H%M%S', '%Y-%m-%d-%H-%M') }}"
    )

    # Tarefa t1: Gera novos logs chamando um script Bash externo
    t1 = BashOperator(
        task_id="generate_new_logs",
        bash_command="./scripts/generate_new_logs.sh",
        params={'filename': 'log.csv'}  # Passa parâmetros para o script
    )

    # Tarefa t2: Verifica se o arquivo de log existe no diretório definido dinamicamente
    t2 = BashOperator(
        task_id="logs_exist",
        bash_command="test -f " + TEMPLATED_LOG_DIR + "log.csv",
    )

    # Tarefa t3: Processa os logs chamando uma função Python
    t3 = PythonOperator(
        task_id="process_logs",
        python_callable=process_logs_func,  # Chama a função externa para processar os logs
        provide_context=True,  # Passa o contexto da execução para a função Python
        templates_dict={'log_dir': TEMPLATED_LOG_DIR},  # Passa o diretório dos logs usando templating
        params={'filename': 'log.csv'}  # Parâmetro adicional para a função
    )

    # Definição da ordem das tarefas:
    # - t0 exibe o timestamp e depois gera novos logs (t1)
    # - t1 gera os logs e depois verifica se o arquivo existe (t2)
    # - t2 verifica a existência do log antes de processá-lo (t3)
    t0 >> t1 >> t2 >> t3

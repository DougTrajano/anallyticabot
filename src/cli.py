import typer
from subprocess import Popen, PIPE
from pathlib import Path
from worker.tasks.factory import TaskFactory

cli = typer.Typer()

@cli.command()
def frontend(
    port: int = 8501,
    enable_cors: bool = True,
    enable_xsr: bool = False):
    """Starts the frontend server (streamlit)

    Args:
    - port: Port to run the frontend server on
    - enable_cors: Enable CORS
    - enable_xsr: Enable XSRF
    """
    typer.echo("Starting frontend server...")

    process = Popen(
        [
            "streamlit",
            "run",
            "Home.py",
            "--server.port",
            str(port),
            f"--server.enableCORS={str(enable_cors).lower()}",
            f"--server.enableXsrfProtection={str(enable_xsr).lower()}",
            f"--server.runOnSave=true"
        ],
        stdout=PIPE,
        cwd=Path("src/app").absolute().as_posix()
    )

    output, error = process.communicate()
    typer.echo(output.decode("utf-8"))

@cli.command()
def backend(
    host: str = "0.0.0.0",
    port: int = 8000):
    """Starts the backend server (FastAPI)

    Args:
    - host: Host to run the backend server on
    - port: Port to run the backend server on
    """
    typer.echo("Starting backend server...")

    process = Popen(
        [
            "uvicorn",
            "api.main:app",
            "--host",
            host,
            "--port",
            str(port),
            "--reload"
        ],
        stdout=PIPE,
        cwd=Path("src").absolute().as_posix()
    )

    output, error = process.communicate()
    typer.echo(output.decode("utf-8"))

@cli.command()
def worker(
    task_name: str = typer.Option(),
    task_id: str = typer.Option()):
    """Starts a worker process for a task.

    Args:
    - task-name: The name of the task.
    - task-id: The ID of the task.
    """
    typer.echo(f"Starting worker for task {task_name} (id: {task_id}).")
    task = TaskFactory.create_executor(task_id, task_name)
    typer.echo(f"Running task {task.__class__.__name__} (id: {task.id}).")
    task._run()
    typer.echo(f"Task {task_name} (id: {task_id}) completed.")

@cli.command()
def alembic(
    command: str = typer.Option(),
    message: str = typer.Option("No message provided.")):
    """Runs alembic commands.

    Args:
    - command: The command to run.
    - message: The message to use for the migration.
    """
    typer.echo("Running alembic commands...")
    process = Popen(
        [
            "alembic",
            command,
            "-m",
            message
        ],
        stdout=PIPE,
        cwd=Path("src").absolute().as_posix()
    )

    output, error = process.communicate()
    typer.echo(output.decode("utf-8"))

if __name__ == "__main__":
    cli()

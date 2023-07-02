# Getting Started

Pending

## Architecture

Pending

## Running the docker container

### frontend

```bash
docker run -d -p 80:80 --name frontend anallyticabot frontend
```

### backend

```bash
docker run -d -p 5000:5000 --name backend anallyticabot backend
```

### worker

```bash
docker run -d --name worker anallyticabot worker
```

**Arguments**

`--task-name` The name of the task you want to run.

`--task-id` The task id registered in the database (API).
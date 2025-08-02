How launch the project?

1) up containers by this command

       docker compose --env-file .template.env.docker up -d

2) and open this link http://0.0.0.0:8000/



How to test this?

1) firstly up test containers

        docker compose -f tests/docker-compose.test.yaml --env-file tests/.env.docker up -d

2) run tests

        pytest

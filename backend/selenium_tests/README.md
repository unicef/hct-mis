# Dev

How to call the tests (from root of the project):

```bash
docker compose -f compose.selenium.yml build ; docker compose -f compose.selenium.yml run --rm selenium
```

How to simulate a CI run (from `deployment` dir):
```bash
sh -c "cd .. && docker build . -f ./docker/Dockerfile --target dev --tag unicef/hct-mis-backend-dev && docker build . -f ./docker/Dockerfile --target dist --tag unicef/hct-mis-backend-dist" && dev_backend_image=unicef/hct-mis-backend-dev dist_backend_image=unicef/hct-mis-backend-dist docker compose -f docker-compose.selenium.yml run --build --rm selenium; dev_backend_image=unicef/hct-mis-backend-dev dist_backend_image=unicef/hct-mis-backend-dist docker compose -f docker-compose.selenium.yml down --remove-orphans
```
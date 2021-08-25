# Build frontend image
```sh
# Ensure you're in the root directory of this repo.
docker build -f deployment/frontend/Dockerfile . -t stateflow-frontend
```
If you want to make the Pyflink image:
```sh
# Ensure you're in the root directory of this repo.
docker build -f deployment/frontend/Dockerfile-pyflink . -t stateflow-frontend-pyflink
```
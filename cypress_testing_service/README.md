# Overview

This service helps in E2E testing of the web application. It supports running it in headless mode in a local development environment or as part of a CI/CD environment.

Example spec files: https://github.com/cypress-io/cypress-example-kitchensink/tree/master/cypress/integration/examples

Example commands: https://example.cypress.io/


## Local development / testing

Turn on the services by calling

```
docker-compose up -d --build
```

And turn on the FE in `frontend` directory:

```
yarn && yarn start
```

When all is up (accessible via `localhost:8082`), you can run the tests by calling in `cypress_testing_service` dir (after calling `yarn`):

```
yarn cy:run
```

Or by opening the window to play with it in the browser:

```
yarn cy:open
```
#!/bin/bash

set -eu

curl -X POST localhost:8082/api/cypress-xlsx/$1

cp ../backend/generated/* cypress/fixtures/
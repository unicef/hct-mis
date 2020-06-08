#!/usr/bin/env bash

export PGPASSWORD=$POSTGRES_CASHASSIST_DATAHUB_PASSWORD

psql -h "$POSTGRES_CASHASSIST_DATAHUB_HOST" \
     -d "$POSTGRES_CASHASSIST_DATAHUB_DB" \
     -U "$POSTGRES_CASHASSIST_DATAHUB_USER" \
     -c "CREATE SCHEMA IF NOT EXISTS ca" \
     -c "CREATE SCHEMA IF NOT EXISTS mis" \
     -c "CREATE SCHEMA IF NOT EXISTS erp"
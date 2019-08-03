#!/usr/bin/env bash

kubectl apply -f redis-deployment.yaml
kubectl apply -f redis-service.yaml
kubectl apply -f token-deployment.yaml
kubectl apply -f token-service.yaml

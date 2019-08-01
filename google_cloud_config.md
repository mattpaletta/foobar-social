# Configuration
We want to use kubernetes on Google Cloud.  Since we both have limited knowledge of kubernetes, we wanted to test it with a single VM on google cloud, using minikube, and then try it on the hosted Kubernetes cluster.

### Installing 
We started a `f1-micro (1 vCPU, 0.6 GB memory)` instance with ubuntu 18.04 LTS with 30 GB of hard drive storage.  This means the instance is wihtin the free tier on google cloud. :) 
* Install docker on the instance:
https://phoenixnap.com/kb/how-to-install-docker-on-ubuntu-18-04

* Install minikube:
```{bash}
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
  && chmod +x minikube
sudo install minikube /usr/local/bin
sudo minikube start --vm-driver=none
```

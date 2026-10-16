# Isolated failure exercises

These manifests create separate lab resources. They do not change the application deployments or service selectors. Use only in your demonstration namespace.

## Image pull failure

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n lastbite -l app=lastbite-lab-image
kubectl describe pod -n lastbite -l app=lastbite-lab-image
kubectl get events -n lastbite --sort-by=.lastTimestamp
```

The missing image intentionally causes `ErrImagePull` / `ImagePullBackOff`. Check registry owner, repository, tag, package visibility and image pull credentials. For the exercise, replace the lab image with your successful backend SHA, or delete the lab resource after explaining the diagnosis:

```bash
kubectl delete -f troubleshooting/broken-image.yaml
```

## Service with no endpoints

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get pods -n lastbite --show-labels
kubectl get endpointslice -n lastbite -l kubernetes.io/service-name=lastbite-lab-service
kubectl describe svc lastbite-lab-service -n lastbite
```

The selector matches no pod labels. Repair only the lab service selector to `app.kubernetes.io/instance=lastbite` and `app.kubernetes.io/component=backend`, then inspect its EndpointSlices. Remove the exercise:

```bash
kubectl delete -f troubleshooting/broken-service.yaml
```

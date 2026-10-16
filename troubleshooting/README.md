# Isolated failure exercises

These manifests create separate lab resources. They do not change the application deployments or service selectors. Use only in your demonstration namespace.

## Image pull failure

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n relaydesk -l app=relaydesk-lab-image
kubectl describe pod -n relaydesk -l app=relaydesk-lab-image
kubectl get events -n relaydesk --sort-by=.lastTimestamp
```

The missing image intentionally causes `ErrImagePull` / `ImagePullBackOff`. Check registry owner, repository, tag, package visibility and image pull credentials. For the exercise, replace the lab image with your successful backend SHA, or delete the lab resource after explaining the diagnosis:

```bash
kubectl delete -f troubleshooting/broken-image.yaml
```

## Service with no endpoints

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get pods -n relaydesk --show-labels
kubectl get endpointslice -n relaydesk -l kubernetes.io/service-name=relaydesk-lab-service
kubectl describe svc relaydesk-lab-service -n relaydesk
```

The selector matches no pod labels. Repair only the lab service selector to `app.kubernetes.io/instance=relaydesk` and `app.kubernetes.io/component=backend`, then inspect its EndpointSlices. Remove the exercise:

```bash
kubectl delete -f troubleshooting/broken-service.yaml
```

# Your remaining steps

1. **Record your presentation.** Present [the slides](../demo/slides.pdf) first. Then follow [the recording guide](../demo/RECORDING.md) to show the app, a live CI run, AWS, Argo CD, Kubernetes, Prometheus, and Grafana. Explain the [security results](SECURITY-RESULTS.md) in your own words. Capture pytest and Compose terminal screenshots while recording.
2. **Upload the recording.** Put the narrated MP4 in a GitHub release (or `demo/` if it fits GitHub's file limit). Link it from the README. The prepared screenshots and automated browser clips do not replace your narration.
3. **Check the submitted link.** You confirmed the form is submitted; make sure it points to `https://github.com/THRISHAL12345/lastbite`.

Ask to prepare the recording environment when you are ready. AWS resources should be created only for the demonstration and removed afterward. [Deployment instructions](DEPLOYMENT.md) contain the repeatable commands. The AWS CLI profile is still called `relaydesk`.

## Login reference

- AWS Console: use your existing `relaydesk-admin` sign-in. Terraform uses the AWS CLI profile and has no separate login.
- Grafana: local admin credentials come from the deployment's `monitoring-grafana` Kubernetes secret; no Grafana Cloud account is needed.
- Argo CD: local admin credentials come from `argocd-initial-admin-secret`.
- Prometheus: no login in this private demo.

With the correct demo kubeconfig selected, retrieve passwords in a private terminal **before** starting a recording:

```bash
kubectl get secret monitoring-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 --decode; echo
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 --decode; echo
```

Both initial usernames are `admin`. Never commit these passwords or show them in your video.

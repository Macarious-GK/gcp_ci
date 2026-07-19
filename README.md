# gcp_ci


## Cloud build stage 
- 1 Checkout repo
- 2 Install dependances and test it ✅
- 3 Test the app --> save outpouts to speskfic folder ✅
- 4 Build image  ✅
- 5 Scan image with trivy --> save outputs to spesific folder then put on a bucket ✅
- 6 Push image to ar ✅
- 7 Deploy to cloudrun
- 8 Deploy to k8s [argocd or manual yaml ] 


```bash
docker build -t europe-west4-docker.pkg.dev/project-be3586ae-547c-413e-aac/warmup2first/fastapi_otp .
gcloud builds submit --tag europe-west4-docker.pkg.dev/project-be3586ae-547c-413e-aac/warmup2first/fastapi_otp


gcloud builds submit --region=europe-west4 --config cloudbuild.yaml
```
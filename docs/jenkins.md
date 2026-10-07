# Jenkins Guide

1. Install Jenkins locally or in Docker.
2. Create a pipeline job from the Jenkinsfile.
3. Ensure Docker and kubectl are installed on the runner.
4. Run the pipeline.

The pipeline checks out code, installs dependencies, runs linting, tests execution, builds images, and deploys manifests.

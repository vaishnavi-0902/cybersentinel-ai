pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'python -m pip install -r requirements.txt'
      }
    }

    stage('Lint') {
      steps {
        sh 'python -m ruff check .'
      }
    }

    stage('Test') {
      steps {
        sh 'python -m pytest -q'
      }
    }

    stage('Build Images') {
      steps {
        sh 'docker build -t cybersentinel-backend .'
        sh 'docker build -f Dockerfile.frontend -t cybersentinel-frontend .'
      }
    }

    stage('Deploy') {
      steps {
        sh 'kubectl apply -f k8s/'
      }
    }
  }
}

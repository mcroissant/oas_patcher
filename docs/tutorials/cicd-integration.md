# CI/CD Integration

Integrating OAS Patcher into your CI/CD pipeline enables automated API specification management, ensuring consistency across environments and reducing manual deployment errors. This tutorial covers comprehensive CI/CD integration strategies for various platforms.

## Prerequisites

- Completed [Multi-Environment Setup](multi-environment.md) tutorial
- Understanding of CI/CD concepts
- Access to a CI/CD platform (GitHub Actions, GitLab CI, Jenkins, etc.)
- Basic knowledge of environment variables and secrets management

## Tutorial Overview

In this tutorial, we'll:
1. Set up automated API specification generation
2. Implement validation and testing workflows
3. Configure environment-specific deployments
4. Add security and secrets management
5. Create deployment approval workflows
6. Implement rollback strategies

## Step 1: Repository Structure for CI/CD

Organize your repository for efficient CI/CD processing:

```
api-project/
├── .github/workflows/          # GitHub Actions workflows
├── .gitlab-ci.yml             # GitLab CI configuration
├── api/
│   ├── base-api.yaml          # Base OpenAPI specification
│   └── schemas/               # Shared schemas
├── bundles/
│   ├── development/
│   │   ├── bundle.yaml
│   │   └── overlays/
│   ├── staging/
│   │   ├── bundle.yaml
│   │   └── overlays/
│   └── production/
│   │   ├── bundle.yaml
│   │   └── overlays/
├── generated/                 # Generated API specifications
├── scripts/
│   ├── build-api.sh          # Build script
│   ├── validate-api.sh       # Validation script
│   └── deploy-api.sh         # Deployment script
└── tests/
    └── api/                   # API tests
```

## Step 2: GitHub Actions Integration

### Basic Workflow

Create `.github/workflows/api-ci.yml`:

```yaml
name: API CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    paths: 
      - 'api/**'
      - 'bundles/**'
  pull_request:
    branches: [main]
    paths:
      - 'api/**'
      - 'bundles/**'

env:
  PYTHON_VERSION: '3.9'

jobs:
  validate:
    name: Validate API Specifications
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Install dependencies
      run: |
        pip install oas-patch
        pip install openapi-spec-validator
        
    - name: Validate base API
      run: |
        openapi-spec-validator api/base-api.yaml
        
    - name: Validate overlays
      run: |
        find bundles -name "*.yaml" -path "*/overlays/*" -exec oas-patch validate {} \;
        
    - name: Validate bundle configurations
      run: |
        find bundles -name "bundle.yaml" -exec oas-patch bundle validate {} \;

  build:
    name: Build API Specifications
    runs-on: ubuntu-latest
    needs: validate
    strategy:
      matrix:
        environment: [development, staging, production]
        
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Install OAS Patcher
      run: pip install oas-patch
      
    - name: Build API for ${{ matrix.environment }}
      run: |
        mkdir -p generated
        oas-patch bundle apply api/base-api.yaml bundles/${{ matrix.environment }} \
          --environment ${{ matrix.environment }} \
          --variable build_timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
          --variable build_number="${{ github.run_number }}" \
          --variable git_commit="${{ github.sha }}" \
          -o generated/api-${{ matrix.environment }}.yaml
          
    - name: Validate generated API
      run: |
        openapi-spec-validator generated/api-${{ matrix.environment }}.yaml
        
    - name: Upload API artifact
      uses: actions/upload-artifact@v4
      with:
        name: api-${{ matrix.environment }}
        path: generated/api-${{ matrix.environment }}.yaml
        retention-days: 30

  test:
    name: Test API Specifications
    runs-on: ubuntu-latest
    needs: build
    strategy:
      matrix:
        environment: [development, staging]
        
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Download API artifact
      uses: actions/download-artifact@v4
      with:
        name: api-${{ matrix.environment }}
        path: generated/
        
    - name: Set up Node.js for API testing
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install testing tools
      run: |
        npm install -g @apidevtools/swagger-parser
        npm install -g spectral-cli
        
    - name: Parse API specification
      run: |
        swagger-parser validate generated/api-${{ matrix.environment }}.yaml
        
    - name: Lint API specification
      run: |
        spectral lint generated/api-${{ matrix.environment }}.yaml \
          --ruleset=spectral:oas --format=github-actions
          
    - name: Security scan
      run: |
        # Install and run security scanner
        npm install -g @42crunch/api-security-audit
        api-security-audit generated/api-${{ matrix.environment }}.yaml

  deploy-dev:
    name: Deploy to Development
    runs-on: ubuntu-latest
    needs: [build, test]
    if: github.ref == 'refs/heads/develop'
    environment: development
    
    steps:
    - name: Download API artifact
      uses: actions/download-artifact@v4
      with:
        name: api-development
        path: generated/
        
    - name: Deploy to development
      run: |
        echo "Deploying to development environment..."
        # Add your deployment commands here
        # Example: kubectl apply -f generated/api-development.yaml
        
    - name: Update API documentation
      run: |
        echo "Updating development API docs..."
        # Example: Update Swagger UI or API portal

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build, test]
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
    - name: Download API artifact
      uses: actions/download-artifact@v4
      with:
        name: api-staging
        path: generated/
        
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # Add your deployment commands here
        
    - name: Run integration tests
      run: |
        echo "Running integration tests against staging..."
        # Add integration test commands

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [deploy-staging]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Download API artifact
      uses: actions/download-artifact@v4
      with:
        name: api-production
        path: generated/
        
    - name: Deploy to production
      env:
        PROD_API_KEY: ${{ secrets.PROD_API_KEY }}
        PROD_SERVER_URL: ${{ secrets.PROD_SERVER_URL }}
      run: |
        echo "Deploying to production environment..."
        # Add your production deployment commands here
        
    - name: Verify deployment
      run: |
        echo "Verifying production deployment..."
        # Add verification commands
```

### Advanced Workflow with Matrix Strategy

Create `.github/workflows/api-matrix.yml` for more complex scenarios:

```yaml
name: API Matrix Deployment

on:
  workflow_dispatch:
    inputs:
      environments:
        description: 'Environments to deploy (comma-separated)'
        required: true
        default: 'development,staging'
      api_version:
        description: 'API version to deploy'
        required: true
        default: 'v1.0.0'

jobs:
  matrix-deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: ${{ fromJson(github.event.inputs.environments) }}
        region: [us-east-1, us-west-2, eu-west-1]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup OAS Patcher
      run: pip install oas-patch
      
    - name: Build region-specific API
      run: |
        oas-patch bundle apply api/base-api.yaml bundles/${{ matrix.environment }} \
          --environment ${{ matrix.environment }} \
          --variable api_version="${{ github.event.inputs.api_version }}" \
          --variable region="${{ matrix.region }}" \
          --variable deployment_region="${{ matrix.region }}" \
          -o api-${{ matrix.environment }}-${{ matrix.region }}.yaml
          
    - name: Deploy to ${{ matrix.environment }} in ${{ matrix.region }}
      run: |
        echo "Deploying to ${{ matrix.environment }} in ${{ matrix.region }}"
        # Add region-specific deployment logic
```

## Step 3: GitLab CI Integration

Create `.gitlab-ci.yml`:

```yaml
stages:
  - validate
  - build
  - test
  - deploy-dev
  - deploy-staging
  - deploy-production

variables:
  PYTHON_VERSION: "3.9"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

before_script:
  - python -m venv venv
  - source venv/bin/activate
  - pip install oas-patch openapi-spec-validator

validate-api:
  stage: validate
  script:
    - openapi-spec-validator api/base-api.yaml
    - find bundles -name "*.yaml" -path "*/overlays/*" -exec oas-patch validate {} \;
    - find bundles -name "bundle.yaml" -exec oas-patch bundle validate {} \;
  rules:
    - changes:
        - api/**/*
        - bundles/**/*

.build-template: &build-template
  stage: build
  script:
    - mkdir -p generated
    - |
      oas-patch bundle apply api/base-api.yaml bundles/$ENVIRONMENT \
        --environment $ENVIRONMENT \
        --variable build_timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        --variable build_number="$CI_PIPELINE_ID" \
        --variable git_commit="$CI_COMMIT_SHA" \
        -o generated/api-$ENVIRONMENT.yaml
    - openapi-spec-validator generated/api-$ENVIRONMENT.yaml
  artifacts:
    paths:
      - generated/api-$ENVIRONMENT.yaml
    expire_in: 1 week

build-development:
  <<: *build-template
  variables:
    ENVIRONMENT: development
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

build-staging:
  <<: *build-template
  variables:
    ENVIRONMENT: staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

build-production:
  <<: *build-template
  variables:
    ENVIRONMENT: production
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

test-api:
  stage: test
  dependencies:
    - build-development
    - build-staging
  script:
    - npm install -g @apidevtools/swagger-parser spectral-cli
    - find generated -name "*.yaml" -exec swagger-parser validate {} \;
    - find generated -name "*.yaml" -exec spectral lint {} --ruleset=spectral:oas \;

deploy-development:
  stage: deploy-dev
  dependencies:
    - build-development
  environment:
    name: development
    url: https://dev-api.example.com
  script:
    - echo "Deploying to development..."
    # Add deployment commands
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

deploy-staging:
  stage: deploy-staging
  dependencies:
    - build-staging
  environment:
    name: staging
    url: https://staging-api.example.com
  script:
    - echo "Deploying to staging..."
    # Add deployment commands
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy-production:
  stage: deploy-production
  dependencies:
    - build-production
  environment:
    name: production
    url: https://api.example.com
  script:
    - echo "Deploying to production..."
    # Add deployment commands
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  when: manual
```

## Step 4: Jenkins Pipeline

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['development', 'staging', 'production'],
            description: 'Target environment'
        )
        string(
            name: 'API_VERSION',
            defaultValue: 'v1.0.0',
            description: 'API version to deploy'
        )
    }
    
    environment {
        PYTHON_VERSION = '3.9'
        PATH = "${env.WORKSPACE}/venv/bin:${env.PATH}"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install oas-patch openapi-spec-validator
                '''
            }
        }
        
        stage('Validate') {
            parallel {
                stage('Validate Base API') {
                    steps {
                        sh 'openapi-spec-validator api/base-api.yaml'
                    }
                }
                stage('Validate Overlays') {
                    steps {
                        sh '''
                            find bundles -name "*.yaml" -path "*/overlays/*" \
                                -exec oas-patch validate {} \\;
                        '''
                    }
                }
                stage('Validate Bundles') {
                    steps {
                        sh '''
                            find bundles -name "bundle.yaml" \
                                -exec oas-patch bundle validate {} \\;
                        '''
                    }
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    def environments = params.ENVIRONMENT ? [params.ENVIRONMENT] : ['development', 'staging', 'production']
                    
                    environments.each { env ->
                        sh """
                            mkdir -p generated
                            oas-patch bundle apply api/base-api.yaml bundles/${env} \
                                --environment ${env} \
                                --variable api_version='${params.API_VERSION}' \
                                --variable build_number='${env.BUILD_NUMBER}' \
                                --variable git_commit='${env.GIT_COMMIT}' \
                                -o generated/api-${env}.yaml
                        """
                        
                        sh "openapi-spec-validator generated/api-${env}.yaml"
                    }
                }
                
                archiveArtifacts artifacts: 'generated/*.yaml', fingerprint: true
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    npm install -g @apidevtools/swagger-parser spectral-cli
                    find generated -name "*.yaml" -exec swagger-parser validate {} \\;
                    find generated -name "*.yaml" -exec spectral lint {} --ruleset=spectral:oas \\;
                '''
            }
        }
        
        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def targetEnv = params.ENVIRONMENT ?: (env.BRANCH_NAME == 'main' ? 'staging' : 'development')
                    
                    if (targetEnv == 'production') {
                        input message: 'Deploy to production?', ok: 'Deploy'
                    }
                    
                    sh "echo 'Deploying to ${targetEnv}...'"
                    // Add deployment commands here
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            emailext (
                subject: "API Deployment Successful - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "API deployment completed successfully for ${params.ENVIRONMENT}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            emailext (
                subject: "API Deployment Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "API deployment failed. Check the build logs for details.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

## Step 5: Environment Variables and Secrets Management

### GitHub Actions Secrets

Configure secrets in your GitHub repository:

```yaml
# In your workflow file
env:
  # Environment-specific variables
  DEV_API_URL: ${{ vars.DEV_API_URL }}
  STAGING_API_URL: ${{ vars.STAGING_API_URL }}
  PROD_API_URL: ${{ secrets.PROD_API_URL }}
  
  # Sensitive data
  DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
  API_SECRET_KEY: ${{ secrets.API_SECRET_KEY }}
  
  # Build metadata
  BUILD_TIMESTAMP: ${{ github.event.head_commit.timestamp }}
  BUILD_NUMBER: ${{ github.run_number }}
  GIT_COMMIT: ${{ github.sha }}
```

### Environment-Specific Overlays with Secrets

Create overlays that use CI/CD environment variables:

```yaml
# overlays/ci-secrets.yaml
overlay: 1.0.0
info:
  title: CI/CD Secrets Configuration
actions:
  - target: "$.components.securitySchemes.DatabaseAuth"
    update:
      type: apiKey
      in: header
      name: X-Database-Token
      x-secret-ref: "{{ env('DATABASE_TOKEN') }}"
      
  - target: "$.info.x-deployment"
    update:
      build_number: "{{ env('BUILD_NUMBER') }}"
      commit_sha: "{{ env('GIT_COMMIT') }}"
      build_timestamp: "{{ env('BUILD_TIMESTAMP') }}"
      pipeline_url: "{{ env('GITHUB_SERVER_URL') }}/{{ env('GITHUB_REPOSITORY') }}/actions/runs/{{ env('GITHUB_RUN_ID') }}"
```

### Vault Integration

For HashiCorp Vault integration:

```bash
#!/bin/bash
# scripts/deploy-with-vault.sh

# Authenticate with Vault
vault auth -method=aws

# Retrieve secrets
export DATABASE_URL=$(vault kv get -field=url secret/database)
export API_SECRET=$(vault kv get -field=secret secret/api)

# Apply bundle with secrets
oas-patch bundle apply api/base-api.yaml bundles/production \
  --environment production \
  --variable database_url="$DATABASE_URL" \
  --variable api_secret="$API_SECRET" \
  -o generated/api-production.yaml
```

## Step 6: Automated Testing Integration

### Contract Testing

Integrate with Pact or similar tools:

```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests

on:
  pull_request:
    paths: ['api/**', 'bundles/**']

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Generate API for testing
      run: |
        pip install oas-patch
        oas-patch bundle apply api/base-api.yaml bundles/development \
          --environment development \
          -o generated/api-test.yaml
          
    - name: Run contract tests
      run: |
        # Install Pact CLI
        npm install -g @pact-foundation/pact-cli
        
        # Run consumer tests
        pact-broker can-i-deploy \
          --pacticipant="api-consumer" \
          --version="$GITHUB_SHA" \
          --to="test"
```

### API Specification Testing

```bash
#!/bin/bash
# scripts/test-api-specs.sh

set -e

echo "Testing API specifications..."

# Test each environment configuration
for env in development staging production; do
    echo "Testing $env environment..."
    
    # Generate API specification
    oas-patch bundle apply api/base-api.yaml bundles/$env \
        --environment $env \
        -o generated/api-$env.yaml
    
    # Validate specification
    openapi-spec-validator generated/api-$env.yaml
    
    # Lint specification
    spectral lint generated/api-$env.yaml --ruleset=spectral:oas
    
    # Security scan
    api-security-audit generated/api-$env.yaml
    
    echo "✓ $env environment tests passed"
done

echo "All API specification tests passed!"
```

## Step 7: Deployment Strategies

### Blue-Green Deployment

```yaml
# .github/workflows/blue-green-deploy.yml
name: Blue-Green Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        required: true
        type: choice
        options: [staging, production]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Generate API specification
      run: |
        pip install oas-patch
        oas-patch bundle apply api/base-api.yaml bundles/${{ inputs.environment }} \
          --environment ${{ inputs.environment }} \
          --variable deployment_strategy="blue-green" \
          --variable deployment_id="${{ github.run_id }}" \
          -o api-${{ inputs.environment }}.yaml
    
    - name: Deploy to green environment
      run: |
        echo "Deploying to green environment..."
        # Deploy to green environment
        
    - name: Run health checks
      run: |
        echo "Running health checks on green environment..."
        # Health check commands
        
    - name: Switch traffic to green
      run: |
        echo "Switching traffic from blue to green..."
        # Traffic switching commands
        
    - name: Cleanup blue environment
      run: |
        echo "Cleaning up blue environment..."
        # Cleanup commands
```

### Canary Deployment

```bash
#!/bin/bash
# scripts/canary-deploy.sh

ENVIRONMENT=${1:-staging}
CANARY_PERCENTAGE=${2:-10}

echo "Starting canary deployment to $ENVIRONMENT with $CANARY_PERCENTAGE% traffic..."

# Generate canary configuration
oas-patch bundle apply api/base-api.yaml bundles/$ENVIRONMENT \
    --environment $ENVIRONMENT \
    --variable deployment_type="canary" \
    --variable canary_percentage="$CANARY_PERCENTAGE" \
    -o api-$ENVIRONMENT-canary.yaml

# Deploy canary version
kubectl apply -f api-$ENVIRONMENT-canary.yaml

# Monitor metrics for 10 minutes
echo "Monitoring canary deployment..."
sleep 600

# Check success metrics
ERROR_RATE=$(curl -s "http://monitoring.example.com/metrics/error_rate")
if (( $(echo "$ERROR_RATE < 0.01" | bc -l) )); then
    echo "Canary deployment successful. Promoting to full deployment..."
    # Promote canary to full deployment
else
    echo "Canary deployment failed. Rolling back..."
    # Rollback canary deployment
fi
```

## Step 8: Monitoring and Observability

### Deployment Monitoring

```yaml
# .github/workflows/deployment-monitoring.yml
name: Post-Deployment Monitoring

on:
  workflow_run:
    workflows: ["API CI/CD Pipeline"]
    types: [completed]

jobs:
  monitor:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    
    steps:
    - name: Wait for deployment stabilization
      run: sleep 300  # Wait 5 minutes
      
    - name: Check API health
      run: |
        for endpoint in ${{ vars.HEALTH_CHECK_ENDPOINTS }}; do
          echo "Checking $endpoint..."
          curl -f $endpoint/health || exit 1
        done
        
    - name: Validate API responses
      run: |
        # Run smoke tests against deployed API
        npm install -g newman
        newman run tests/api-smoke-tests.json \
          --environment tests/environments/production.json
        
    - name: Check performance metrics
      run: |
        # Query monitoring system for performance metrics
        python scripts/check-performance-metrics.py \
          --threshold-p95=500 \
          --threshold-error-rate=0.01
```

## Step 9: Rollback Strategies

### Automated Rollback

```bash
#!/bin/bash
# scripts/rollback.sh

ENVIRONMENT=${1:-production}
PREVIOUS_VERSION=${2}

echo "Rolling back $ENVIRONMENT to version $PREVIOUS_VERSION..."

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Finding previous successful deployment..."
    PREVIOUS_VERSION=$(curl -s "http://deployment-tracker.example.com/api/previous-version/$ENVIRONMENT")
fi

echo "Rolling back to version: $PREVIOUS_VERSION"

# Retrieve previous configuration
git checkout $PREVIOUS_VERSION -- bundles/$ENVIRONMENT/

# Regenerate API specification
oas-patch bundle apply api/base-api.yaml bundles/$ENVIRONMENT \
    --environment $ENVIRONMENT \
    --variable rollback_version="$PREVIOUS_VERSION" \
    --variable rollback_timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -o api-$ENVIRONMENT-rollback.yaml

# Deploy rollback version
kubectl apply -f api-$ENVIRONMENT-rollback.yaml

echo "Rollback completed successfully"
```

## Best Practices for CI/CD Integration

### 1. Environment Parity

Ensure your CI/CD environments match production as closely as possible:

```yaml
# Use consistent configuration across environments
variables:
  base_configuration: &base_config
    timeout: 30
    retry_count: 3
    
development:
  <<: *base_config
  debug_mode: true
  
production:
  <<: *base_config
  debug_mode: false
```

### 2. Security Scanning

Always include security scanning in your pipeline:

```bash
# Install security tools
npm install -g @42crunch/api-security-audit
pip install safety bandit

# Scan API specification
api-security-audit generated/api-production.yaml

# Scan Python dependencies
safety check
bandit -r src/
```

### 3. Progressive Deployment

Implement progressive deployment strategies:

```yaml
environments:
  development:
    auto_deploy: true
  staging:
    auto_deploy: true
    requires_approval: false
  production:
    auto_deploy: false
    requires_approval: true
    deployment_strategy: "blue-green"
```

### 4. Monitoring Integration

Integrate monitoring from the start:

```yaml
# Add monitoring configuration to overlays
- target: "$.info.x-monitoring"
  update:
    health_check: "/health"
    metrics_endpoint: "/metrics"
    alert_email: "{{ env('ALERT_EMAIL') }}"
    dashboard_url: "{{ env('MONITORING_DASHBOARD_URL') }}"
```

## Next Steps

With CI/CD integration complete, you can:

1. Explore [Advanced Templating](advanced-templating.md) for complex dynamic configurations
2. Set up monitoring and alerting for your deployments
3. Implement automated testing strategies
4. Add security scanning and compliance checks

## Summary

In this tutorial, you learned how to:
- Integrate OAS Patcher with GitHub Actions, GitLab CI, and Jenkins
- Implement automated validation and testing
- Handle secrets and environment variables securely
- Set up deployment strategies and rollback procedures
- Monitor deployments and ensure quality

CI/CD integration with OAS Patcher provides a robust foundation for automated API specification management and deployment.

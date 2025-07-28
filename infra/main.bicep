@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment name (e.g., dev, prod)')
param environmentName string = 'dev'

@description('PostgreSQL administrator login')
param postgresAdminLogin string = 'postgres'

@description('PostgreSQL administrator password')
@secure()
param postgresAdminPassword string

@description('Azure OpenAI deployment name')
param openAiDeploymentName string = 'gpt-4'

@description('Container image for the chat application')
param containerImageName string = 'chatapp:latest'

// Generate unique names using resource tokens
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = {
  'azd-env-name': environmentName
  'project': 'azure-openai-chat'
}

// User-assigned managed identity for secure service-to-service authentication
resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${resourceToken}'
  location: location
  tags: tags
}

// Log Analytics workspace for monitoring and logging
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'law-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Azure OpenAI cognitive services account
resource openAi 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'openai-${resourceToken}'
  location: location
  tags: tags
  kind: 'OpenAI'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userIdentity.id}': {}
    }
  }
  properties: {
    customSubDomainName: 'openai-${resourceToken}'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true // Force use of Azure AD authentication
  }
  sku: {
    name: 'S0'
  }
}

// Azure OpenAI model deployment
resource openAiDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: openAi
  name: openAiDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4'
      version: '1106-Preview'
    }
    raiPolicyName: 'Microsoft.Default'
  }
  sku: {
    name: 'Standard'
    capacity: 10
  }
}

// PostgreSQL flexible server
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: 'psql-${resourceToken}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userIdentity.id}': {}
    }
  }
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: postgresAdminPassword
    version: '16'
    storage: {
      storageSizeGB: 32
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Enabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

// PostgreSQL database
resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: postgresServer
  name: 'chatappdb'
  properties: {
    charset: 'utf8'
    collation: 'en_US.utf8'
  }
}

// PostgreSQL firewall rule to allow Azure services
resource postgresFirewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Container Apps environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${resourceToken}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Container registry for storing application images
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'acr${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userIdentity.id}': {}
    }
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

// Role assignment for managed identity to pull from container registry
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: containerRegistry
  name: guid(containerRegistry.id, userIdentity.id, 'acrpull')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: userIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Role assignment for managed identity to access Azure OpenAI
resource openAiUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: openAi
  name: guid(openAi.id, userIdentity.id, 'cognitiveservicesuser')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908') // Cognitive Services User
    principalId: userIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Container app for the chat application
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-chatapp-${resourceToken}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userIdentity.id}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 5000
        allowInsecure: false
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: userIdentity.id
        }
      ]
      secrets: [
        {
          name: 'postgres-password'
          value: postgresAdminPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'chatapp'
          image: '${containerRegistry.properties.loginServer}/${containerImageName}'
          resources: {
            cpu: 1
            memory: '2Gi'
          }
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: userIdentity.properties.clientId
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openAi.properties.endpoint
            }
            {
              name: 'AZURE_OPENAI_API_VERSION'
              value: '2024-02-01'
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: openAiDeploymentName
            }
            {
              name: 'POSTGRES_HOST'
              value: postgresServer.properties.fullyQualifiedDomainName
            }
            {
              name: 'POSTGRES_DATABASE'
              value: postgresDatabase.name
            }
            {
              name: 'POSTGRES_USER'
              value: postgresAdminLogin
            }
            {
              name: 'POSTGRES_PASSWORD'
              secretRef: 'postgres-password'
            }
            {
              name: 'POSTGRES_PORT'
              value: '5432'
            }
            {
              name: 'POSTGRES_SSL_MODE'
              value: 'require'
            }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: {
                path: '/api/health'
                port: 5000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 30
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/api/health'
                port: 5000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 60
              periodSeconds: 30
              timeoutSeconds: 10
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-rule'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
  dependsOn: [
    acrPullRoleAssignment
    openAiUserRoleAssignment
  ]
}

// Outputs for use by the application and deployment pipeline
output AZURE_OPENAI_ENDPOINT string = openAi.properties.endpoint
output AZURE_OPENAI_DEPLOYMENT_NAME string = openAiDeploymentName
output POSTGRES_HOST string = postgresServer.properties.fullyQualifiedDomainName
output POSTGRES_DATABASE string = postgresDatabase.name
output CONTAINER_REGISTRY_LOGIN_SERVER string = containerRegistry.properties.loginServer
output CONTAINER_APP_FQDN string = containerApp.properties.configuration.ingress.fqdn
output MANAGED_IDENTITY_CLIENT_ID string = userIdentity.properties.clientId
output MANAGED_IDENTITY_ID string = userIdentity.id

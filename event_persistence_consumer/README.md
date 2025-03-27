# Event Persistence Consumer

An Azure Function App with a service bus topic trigger.

This function consumes messages from a "sessionful" service bus topic and
sends them to an Azure SQL Database for persistant storage.

## Pre-requisites

- an Azure Function app
- an Azure service bus namespace
- a service bus topic
- a sessionful subscription on the topic

## Deployment

Deployment can be done from the command line using the
[azure-functions-core-tools](https://github.com/Azure/azure-functions-core-tools) library.

```bash
func azure functionapp publish <app_name>
```

Or from a DevOps pipeline using the AzureFunctionApp task. See example pipeline below.

```yaml
trigger: none
 
variables:
  functionAppName: 'myfunctionapp'
  resourceGroupName: 'myresourcegroup'
  serviceConnection: 'myserviceconnection'
  workingDirectory: '$(System.DefaultWorkingDirectory)/event_persistence_consumer'
  myDestinationFolder: '$(System.ArtifactsDirectory)'
 
stages:
- stage: Build
  displayName: Build Stage
 
  jobs:
  - job: Build
    displayName: Build App
    pool:
      vmImage: 'ubuntu-latest'
 
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: 3.11
    - bash: |
        pip install --target="./.python_packages/lib/site-packages" -r ./requirements.txt
      workingDirectory: $(workingDirectory)
      
    - task: ArchiveFiles@2
      inputs:
        includeRootFolder: false
        rootFolderOrFile: $(workingDirectory)
        archiveType: zip
        archiveFile: $(Build.ArtifactStagingDirectory)/eventpercons.zip
        replaceExistingArchive: true
 
 
    - task: PublishBuildArtifacts@1

    - task: DownloadBuildArtifacts@1
      inputs:
        artifactName: drop

    - task: AzureFunctionApp@2
      displayName: Deploy Function App
      inputs:
        azureSubscription: ${{ variables.serviceConnection }}
        appType: functionAppLinux
        appName: ${{ variables.functionAppName }}
        package: '$(System.ArtifactsDirectory)/drop/eventpercons.zip'
        deployToSlotOrASE: true  
        resourceGroupName: ${{ variables.resourceGroupName }}
        deploymentMethod: 'zipDeploy'
```

### Configuration

The following environment variables need to be set on the function app.

| variable                 | example value                                                                                                                    | description                        |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| SERVICE_BUS              | Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true; | service bus connection string      |
| SERVICE_BUS_TOPIC        | rdf-delta                                                                                                                        | name of service bus topic          |
| SERVICE_BUS_SUBSCRIPTION | event-persistence-consumer                                                                                                       | name of service bus subscription   |
| SqlConnectionString      | DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!;                                   | connection string for the database |

## Local Development

### Setting Up

Set the above environment variables in a local.settings.json like so:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python"
    "SERVICE_BUS": "Endpoint=sb://localhost;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;",
    "SERVICE_BUS_SUBSCRIPTION": "mysubscriptionname",
    "SERVICE_BUS_TOPIC": "mytopicname",
    "SqlConnectionString": "DRIVER={ODBC Driver 17 for SQL Server};SERVER=db,1433;DATABASE=rdf_delta;UID=sa;PWD=P@ssw0rd!;"
  },
  "ConnectionStrings": {}
}
```

You can then run the app locally with

```bash
func start
```

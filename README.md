# Yoga Analyzer App

The main purpose of this project is to combine several concepts of Internet of Things (IOT) with machine learning (ML), particularly deep learning. Following that, we would like to introduce our new app, Yoga Analyzer, which allows yoga practitioners to evaluate themselves immediately after the exercise session is over. In the following part of this section, we will subsequently explain the motivation behind this project, the algorithm we employed, and the dataset we utilized for fine-tuning. 

## Folder Contents

- model-trainings: This folder contains the .ipynb notebooks used during the fine-tuning of our models.

- YogaAnalyzerApp: This folder contains the files required for the app. 

## Details of how to run the project

To build and run the project, you first need to locate to **YogaAnalyzerApp** folder. There are two options to run the project:
1. By installing a virtual environment
2. Via Docker image

### 1. Running the project with virtual environment

To run the project with a virtual environment, a virtual environment with python==3.11 version is required. After the requirements are downloaded in the virtual environment, the following command should be used to run the project.

	streamlit run app.py

With this command, we will connect to localhost in the browser and our app will run.

### 2. Building the project with Docker

> **WARNING:** Since we could not grant camera permission in the Docker image, our application's pose detection via webcam feature may not work if the project is built with Docker. However, you can still examine the application through the demo video we have included in the application.

Dockerfile was created in the folder to build the project with Docker. The following command can be used to build the Docker image.

	docker build -t USER_NAME/REPO_NAME .
  
After the image is built, the following command should be used to run it.

	docker run -p 8501:8501 USER_NAME/REPO_NAME

After this command, you need to connect to **localhost:8501** from the browser to run the app.

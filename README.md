
# Yoga Analyzer App

The main purpose of this project is to combine several concepts of Internet of Things (IOT) with machine learning (ML), particularly deep learning. Following that, we would like to introduce our new app, Yoga Analyzer, which allows yoga practitioners to evaluate themselves immediately after the exercise session is over. In the following part of this section, we will subsequently explain the motivation behind this project, the algorithm we employed, and the dataset we utilized for fine-tuning. 

## Method

The Yoga Analyzer app uses the state-of-the-art You Only Look Once version 8 (YOLOv8) model for yoga routine analysis. Since our goal was to recognize and evaluate various yoga poses performed by a single person during their routine, we used YOLOv8, known for its speed and accuracy, to perform a classification task instead of traditional object detection.

### The Datasets & Fine-Tuned Models

We trained the model using two different datasets that include diverse yoga poses performed by the user. Each image in the datasets is labeled with the corresponding yoga pose. We retrieved both datasets from [Kaggle](https://www.kaggle.com/).

#### Yoga Poses Dataset & Beginner Model

[Yoga Poses Dataset](https://www.kaggle.com/datasets/niharika41298/yoga-poses-dataset) consists of images collected via Bing API. It contains 5 different poses: downdog, goddess, plank, tree, and warrior2. The data is divided into 70\% train and 30\% test and contains 1551 images in total.

YOLOv8's `yolov8n-cls.pt` weights were used for the fine-tuning of the model developed using this data set. The model reached 97.9% top-1 and 99.9% top-5 validation accuracy.

![image](https://github.com/user-attachments/assets/c2863b11-7d39-430a-8039-faffa50f46b3)


#### Yoga Posture Dataset & Advanced Model

[Yoga Posture Dataset](https://www.kaggle.com/datasets/tr1gg3rtrash/yoga-posture-dataset) consists of 2756 images with 47 different yoga poses. Since this data set is not divided into test and train initially, we randomly divided the data set into 70% train and 30% test for each class.

Due to the higher number of classes in the training performed with this data set, the yolov8m-cls.pt pre-trained weight was used, which is larger than the weight used in the 5-class training. For the same reason, the model was fine-tuned for 10 epochs. The model reached 86.6% top-1 and top-5 98.2% validation accuracy.

![image](https://github.com/user-attachments/assets/f8c61f9a-21ee-4759-8c83-37826f7aed0f)

## Yoga Analyzer

### App Interface and Usage

Our app provides basic or detailed analysis based on the selection. If the user is not sure about his/her preferences, we have also covered that. Under each option, there is a description which helps the user to find the appropriate choices and mentions the evaluation criteria.  We also included a duration tolerance slider bar in basic analysis. With this addition, the user can arrange the strictness of the evaluation algorithm.
![image](https://github.com/user-attachments/assets/c939cc93-46f9-4b3f-bdc4-8e77897680c8)
![image](https://github.com/user-attachments/assets/3d1297d5-ad93-4723-80a0-de8437fd4e64)

After arranging the application configurations based on his/her needs, the only thing a user needs to do is to enter the exercises and corresponding durations of the exercise session. There are 5 exercise options in the app for beginners including "downdog", "goddess", "plank", "tree" and "warrior2" and 47 for the advanced yogis. 
![image](https://github.com/user-attachments/assets/71214bbb-07c1-40a1-86cf-e2612ba98994)


If the user tries to start recording without adding the routine, he/she will encounter an error message.
![image](https://github.com/user-attachments/assets/971bd49b-4235-4ac3-b543-577d45105815)

Our app is designed for real-life analysis. In other words, instead of uploading a video recording of an exercise session, our app gets the video recording while the user performing his/her routine. The user can also monitor the poses and durations detected by our app at the end of the exercise session.
![image](https://github.com/user-attachments/assets/d78e538f-b2ba-4ca5-9920-7fc70d79ab3a)

After the session, either an evaluation checklist or a bar chart is provided to the user depending on the analysis selection. The ticks refer to the exercises that are performed correctly and determined based on tolerance settings that are arranged by the user prior to the exercise session.
![image](https://github.com/user-attachments/assets/0e2edce4-4f51-4ee5-b8bb-332805cc37cf)

On the other hand, the bar chart shows the degree of success which is more detailed than a binary decision.
![image](https://github.com/user-attachments/assets/5a3aa2eb-4c97-4093-b127-0480fb6b62b1)

The app includes a demo video for illustration purposes. Similar to the real-time application, while the video is playing,  
our app performs an evaluation process and returns the result in the end of the video.

## Folder Contents

- model-trainings: This folder contains the .ipynb notebooks used during the fine-tuning of our models.

- YogaAnalyzerApp: This folder contains the files required for the app. 

## Details of how to run the project

To build and run the project, you first need to locate to **YogaAnalyzerApp** folder. There are two options to run the project:
1. By installing a virtual environment
2. Via a Docker image

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

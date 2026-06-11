# SILAILENS

## Digital Preservation and Analysis of Temple Sculptures Using Machine Learning

### Overview

SilaiLens is an AI-powered web application developed for the digital preservation and analysis of South Indian temple sculptures. The system automatically identifies ornamental features from temple sculpture images and predicts the corresponding dynasty using deep learning techniques.

The project focuses on sculptures belonging to the Pallava and Chola dynasties and aims to support cultural heritage preservation, historical research, and educational exploration through automated image analysis.

---

## Problem Statement

Temple sculptures contain valuable historical and cultural information through their ornamental features such as:

* Head ornaments
* Weapons
* Waist ornaments
* Leg ornaments

Traditionally, identifying these features and determining the dynasty of a sculpture requires expert knowledge from archaeologists, historians, and heritage researchers. This process is time-consuming and not easily accessible to the general public.

SilaiLens addresses this challenge by providing an automated machine learning-based solution for sculpture analysis and dynasty prediction.

---

## Objectives

* Develop an intelligent web-based application for temple sculpture analysis.
* Detect important ornamental features from sculpture images.
* Classify sculptures into Pallava or Chola dynasties.
* Generate structured metadata for digital preservation.
* Provide historical context related to the predicted dynasty.
* Support cultural heritage documentation and research.

---

## Features

### Dynasty Classification

Predicts whether a sculpture belongs to:

* Pallava Dynasty
* Chola Dynasty

### Ornament Detection

Detects the presence of:

* Head Ornaments
* Weapons
* Waist Ornaments
* Leg Ornaments

### Historical Context Retrieval

Provides dynasty-related historical information alongside predictions.

### Metadata Generation

Creates structured analysis records including:

* Predicted Dynasty
* Confidence Scores
* Detected Ornaments
* Timestamp Information

### User-Friendly Web Interface

Allows users to upload temple sculpture images and receive analysis results instantly.

---

## System Architecture

The system consists of five major layers:

### 1. Image Upload & Preprocessing Layer

* Image Upload
* Resizing
* Normalization
* Image Enhancement

### 2. AI Analysis Layer

* Dynasty Classification Model
* Ornament Detection Model
* Confidence Score Calculation

### 3. Historical Context Layer

* Retrieves dynasty-specific historical information

### 4. Result Presentation Layer

* Displays predictions and detected ornaments

### 5. Metadata & Storage Layer

* Generates JSON metadata
* Stores images and analysis records

---

## Methodology

### Step 1: Data Collection

Temple sculpture images were collected from publicly available online heritage resources, museum archives, and educational reference sources.

### Step 2: Data Preprocessing

Applied preprocessing techniques:

* Resizing
* Normalization
* Rotation
* Flipping
* Brightness Adjustment
* Cropping

### Step 3: Model Development

Deep learning models were developed using transfer learning.

### Step 4: Model Training

Models were trained on the curated sculpture dataset.

### Step 5: Evaluation

Performance was evaluated using classification accuracy metrics.

### Step 6: Deployment

Integrated into a web application using FastAPI and React.js.

---

## Dataset Information

| Parameter           | Value     |
| ------------------- | --------- |
| Total Images        | 158       |
| Pallava Images      | 84        |
| Chola Images        | 74        |
| Ornament Categories | 4         |
| Image Size          | 224 × 224 |

### Ornament Categories

* Head Ornaments
* Weapons
* Waist Ornaments
* Leg Ornaments

---

## Technology Stack

### Programming Languages

* Python
* JavaScript

### Deep Learning & Computer Vision

* TensorFlow
* Keras
* MobileNetV2
* OpenCV

### Backend

* FastAPI

### Frontend

* React.js
* Vite
* Axios

### Database & Storage

* Supabase Database
* Supabase Storage

### Metadata Format

* JSON

---

## Algorithms Used

### Convolutional Neural Networks (CNN)

Used for extracting visual features and image classification.

### MobileNetV2

Lightweight CNN architecture used as the backbone model for:

* Dynasty Classification
* Ornament Detection

### Transfer Learning

Used to improve performance on a limited dataset by leveraging pre-trained models.

---

## Performance Metrics

### Dynasty Classification Accuracy

* Overall Accuracy: 81.2%
* Chola Accuracy: 85.0%
* Pallava Accuracy: 75.0%

### Ornament Detection Accuracy

| Ornament Category | Accuracy |
| ----------------- | -------- |
| Headwear          | 84.4%    |
| Weapons           | 71.9%    |
| Waistbands        | 84.4%    |
| Leg Ornaments     | 65.6%    |

### Average Ornament Detection Accuracy

76.6%

---

## Sample Output

The system generates:

* Predicted Dynasty
* Confidence Score
* Detected Ornaments
* Historical Information
* JSON Metadata

---

## System Limitations

* Supports only Pallava and Chola dynasty sculptures.
* Performance decreases with low-quality images.
* Sensitive to poor lighting and blurred images.
* Does not currently use temple location or inscription information.
* Low-confidence predictions may be less reliable.
* Limited dataset size affects generalization.

---

## Future Enhancements

* Support additional South Indian dynasties.
* Integration of 3D sculpture analysis.
* Cloud-based centralized heritage archive.
* Multi-language support.
* Expert validation by historians and archaeologists.
* Augmented Reality visualization.

---

## Sustainable Development Goals (SDGs)

This project contributes to:

* SDG 4 – Quality Education
* SDG 9 – Industry, Innovation and Infrastructure
* SDG 11 – Sustainable Cities and Communities

---

## Team Members

* Shuguftha Habeeba (24251A05V6)
* Madhuja (24251A05V7)
* Sai Rishitha (24251A05Y1)

---

## Guide

Dr. Raghavender K.V
Associate Professor
Department of Computer Science & Engineering
G. Narayanamma Institute of Technology & Science

---

## Project Title

Digital Preservation and Analysis of Temple Sculptures Using Machine Learning

SilaiLens – AI-Powered Temple Sculpture Analysis and Dynasty Prediction System.

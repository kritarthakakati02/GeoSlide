# 🌍 GeoSlide 

**GeoSlide AI** is a Machine Learning-Based Landslide Risk Assessment System that predicts landslide risk using environmental and geological parameters while providing transparent model explanations through Explainable AI (SHAP) and interactive geospatial visualization.

The project combines machine learning, data visualization, and modern web technologies to create an easy-to-use platform for landslide risk analysis.

---

## Features

- Predict landslide risk using a trained K-Nearest Neighbors (KNN) model
- Explain predictions using SHAP with a Random Forest surrogate model
- Explore historical landslide events through an interactive map
- Analyze the training dataset with interactive visualizations
- Modern multi-page Streamlit dashboard
- FastAPI backend serving machine learning predictions
- Modular project structure for easy maintenance and extension

---

## Technology Stack

### Programming Language
- Python

### Frontend
- Streamlit

### Backend
- FastAPI

### Machine Learning
- Scikit-learn
- SHAP

### Data Processing
- Pandas
- NumPy

### Visualization
- Plotly
- Matplotlib
- Folium

### Development Tools
- Jupyter Notebook
- Joblib

---

## Project Structure

```text
GeoSlide/
│
├── backend/          # FastAPI backend
├── frontend/         # Streamlit dashboard
├── datasets/         # Training and historical datasets
├── models/           # Trained machine learning models
├── notebooks/        # Data analysis and model development
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## How It Works

1. Environmental and geological parameters are provided through the Streamlit interface.
2. The FastAPI backend processes the request.
3. The trained KNN model predicts the landslide risk.
4. A Random Forest surrogate model generates SHAP explanations.
5. Results are displayed with prediction confidence, feature importance, and interactive visualizations.

---

## Machine Learning Models

| Component | Model |
|----------|-------|
| Risk Prediction | K-Nearest Neighbors (KNN) |
| Explainability | Random Forest + SHAP |

---

## Installation

Clone the repository:

```bash
git clone https://github.com/kritarthakakati02/GeoSlide.git

cd GeoSlide
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## Running the Project

### Start the backend

```bash
cd backend

uvicorn app:app --reload
```

### Start the frontend

```bash
cd frontend

streamlit run Home.py
```

The frontend communicates with the FastAPI backend running locally.

---

## Project Modules

- Dashboard
- Landslide Risk Prediction
- SHAP Explainable AI
- Historical Landslide Explorer
- Dataset Analytics
- About

---

## License

This project is licensed under the MIT License.

---

## Developer

**Kritartha Kakati**

B.Tech Computer Science & Engineering

Sikkim Manipal Institute of Technology

Machine Learning | Data Science | Software Development
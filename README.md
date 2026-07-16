# GeoSlide AI

A Machine Learning-Based Landslide Risk Assessment System that leverages geospatial and historical data to assess and visualize landslide risk.

## Features (planned)

- Landslide risk prediction using multiple ML algorithms
- SHAP-based model explainability
- Historical landslide dashboard
- Interactive Streamlit frontend
- FastAPI backend for serving predictions
- NASA and training dataset integration
- Google Colab notebooks for experimentation and model development

## Tech Stack

- **Languages:** Python
- **Machine Learning:** scikit-learn, TensorFlow
- **Explainability:** SHAP
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Data Handling:** pandas, numpy
- **Visualization:** matplotlib, plotly
- **Notebooks:** Jupyter, Google Colab

## Project Structure

```
GeoSlideAI/
│
├── datasets/
│   ├── nasa/
│   └── training/
│
├── notebooks/
├── backend/
├── frontend/
├── models/
├── utils/
├── reports/
│
├── .gitignore
├── README.md
├── requirements.txt
└── LICENSE
```

## Installation

```bash
# Clone the repository
git clone <repository_url>
cd GeoSlideAI

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Future Work

- Data collection and preprocessing pipelines
- Model training and evaluation across multiple ML algorithms
- SHAP explainability integration
- FastAPI backend development
- Streamlit dashboard development
- Deployment

## Project Status

🚧 **Initialization Phase** — Project structure has been created. Development has not yet started.

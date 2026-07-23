# GeoSlide AI

A Machine Learning-Based Landslide Risk Assessment System that leverages geospatial and historical data to assess and visualize landslide risk.

## Features

- Landslide risk prediction served by a trained KNN model
- SHAP-based model explainability (Random Forest explainer)
- Historical landslide dashboard
- Interactive Streamlit frontend
- FastAPI backend for serving predictions
- NASA and training dataset integration
- Jupyter notebooks documenting the full ML pipeline (EDA, preprocessing,
  feature engineering, training, evaluation, SHAP, export)

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
git clone https://github.com/kritarthakakati02/GeoSlide.git
cd GeoSlide

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the App

Two servers need to run side by side:

```bash
# Terminal 1 - backend (FastAPI)
cd backend
uvicorn app:app --reload

# Terminal 2 - frontend (Streamlit)
cd frontend
streamlit run Home.py
```

The frontend talks to the backend at `http://127.0.0.1:8000` by default;
set the `GEOSLIDE_API_URL` environment variable to point it elsewhere.

## Future Work

- Expand SHAP explainability from the notebooks into the live SHAP
  Analysis page
- Build out the Historical Map and Dataset Analytics pages
- Deployment

## Project Status

✅ **Functional** — Backend, frontend, and prediction pipeline are
integrated end-to-end. SHAP Analysis, Historical Map, Dataset Analytics,
and Home (multipage) are scaffolded for future work.

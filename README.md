# Toonify Pro 🎨


Live Demo: https://vaidehijella-toonify-pro-app-wqd44i.streamlit.app/

Toonify Pro is a Streamlit image-transformation application that converts uploaded photos into stylized artwork using OpenCV-based image processing. It includes user authentication, six configurable artistic filters, SQLite-backed activity tracking, real processing-time instrumentation, a personal image album, and Stripe **test-mode** payments for premium downloads.

## Features

- Six image filters: Classic Cartoon, Sketch, Color Pencil, Oil Painting, Watercolor, and Anime Style
- OpenCV edge detection, bilateral filtering, color quantization, blending, and enhancement
- Streamlit authentication and account management
- SQLite storage for users, transactions, albums, and processing metrics
- Real execution timing with `time.perf_counter()`
- Stripe PaymentIntent integration in test mode using Stripe's test PaymentMethod
- Download flows for PNG/JPEG outputs
- Pytest coverage for filter and image-processing modules

## Tech Stack

Python, Streamlit, OpenCV, NumPy, Pillow, scikit-learn, SQLite, bcrypt, Stripe, pytest

## Project Structure

```text
toonify-pro/
├── app.py
├── utils/
│   ├── __init__.py
│   ├── filters.py
│   └── image_processing.py
├── tests/
│   ├── test_filters.py
│   └── test_image_processing.py
├── .streamlit/
│   └── secrets.toml.example
├── .env.example
├── .gitignore
├── requirements.txt
├── style.css
└── README.md
```

## Local Setup

1. Clone the repository and open the folder.
2. Create and activate a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
5. Add your own Stripe **test-mode** publishable and secret keys. Do not use live keys for this portfolio project.
6. Run:

```bash
streamlit run app.py
```

## Stripe Test Mode

The app intentionally accepts only an `sk_test_...` key. The payment demo creates and confirms a Stripe PaymentIntent using Stripe's documented `pm_card_visa` test PaymentMethod. No real money is charged.

Never commit `.streamlit/secrets.toml`, `.env`, the SQLite database, or generated `user_albums/` content. These paths are already excluded by `.gitignore`.

## Processing Metrics

Each successful filter run records its true execution duration, filter name, and input dimensions in the local `processing_metrics` table. This makes performance claims measurable instead of estimated.

## Tests

Run:

```bash
pytest -q
```

## Deployment

This repository is prepared for Streamlit Community Cloud. Add the repository, set `app.py` as the entry point, and paste your Stripe test secrets into the app's Secrets settings instead of committing them.

## Portfolio Notes

For resume or interview claims, use only metrics you actually observe after deployment—for example number of unique testers, images processed, or measured average processing time.

## Author

Vaidehi Jella

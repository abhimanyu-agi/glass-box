"""Agent package — suppresses known-harmless warnings for demo cleanliness."""

import warnings

# Silence the pandas read_sql SQLAlchemy advisory (psycopg2 works fine)
warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy connectable",
    category=UserWarning,
)
# In run.py or the main script where create_app is called
import os
import sys
from app import create_app


if __name__ == "__main__":
    app = create_app()

    app.run(host='0.0.0.0', port=5000, debug=True)

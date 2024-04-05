# IoTApp - Vending Machine with Flask, Paytm, and MySQL

This repository contains code for a vending machine application built using Raspberry Pi, Python, Flask, Paytm API, and MySQL database. The application facilitates automatic vending based on QR code scanning.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.x
- Flask
- Paytm API credentials
- MySQL server

## Setup

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Dhruv7201/IoTApp.git
   ```

2. Navigate to the project directory:

   ```bash
   cd IoTApp
   ```

3. Install dependencies using `pip`:

   ```bash
   pip install -r requirement.txt
   ```

4. Configure Paytm API credentials:

   - Obtain your Paytm API credentials (Merchant ID, Merchant Key, etc.).
   - Update the configuration file (`.env`) with your Paytm API credentials.

## How to Run

1. Activate the virtual environment (if using):

   ```bash
   python -m venv myenv
   ```

   ```bash
   source myenv/bin/activate
   ```

2. Run the Flask application:

   ```bash
   python run.py
   ```

3. Access the application in your web browser:

   ```
   http://localhost:5000
   ```

## Usage

1. Navigate to the home page of the application.

2. Scan the QR code displayed on the vending machine using the Paytm app.

3. Upon successful payment verification, select the desired item from the vending machine interface.

4. The selected item will be dispensed automatically.

## Directory Structure

- `app`: Contains the Flask application code.
- `requirements.txt`: Lists all the dependencies required by the application.
- `run.py`: Entry point of the application.

## Acknowledgments

- Thanks to [Paytm](https://paytm.com/) for providing the payment gateway.
- Inspiration from various vending machine projects available online.

## Troubleshooting

- If you encounter any issues while running the application, please check the console logs for error messages.
- Ensure that all dependencies are installed correctly and the Paytm API credentials are configured properly.
- For database-related issues, verify the database connection settings in `.env` and ensure that the MySQL server is running.
- If the Paytm payment integration is not working, double-check the API credentials and the Paytm developer documentation for troubleshooting tips.

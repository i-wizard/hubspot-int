# HubSpot Integration API

## Project Overview

This project is a FastAPI-based microservice designed to integrate with the HubSpot CRM platform. It provides RESTful API endpoints that allow you to:

- Create or update contacts, deals, and tickets in HubSpot.
- Retrieve CRM objects (contacts, deals, tickets) with pagination and filtering support.
- Link contacts with deals and tickets automatically.

The service abstracts the HubSpot API complexity, offering simplified endpoints for CRM operations and token-based authentication.

---

## Installation and Setup Instructions

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)

### Clone the Repository
```bash
git clone git@github.com:i-wizard/hubspot-int.git
cd hubspot-int
```

### Virtual Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Configuration
Copy `sample.env` to `.env` and configure the variables:
```bash
cp sample.env .env
```

Edit `.env` with your environment-specific settings (see [Environment Variable Configurations](#environment-variable-configurations)).


### Run with Docker
```bash
docker-compose up --build
```

---

## API Endpoints and Their Usage

### Base URL
```
http://localhost:5001
```

### 1. Create or Update Contact
**POST** `/contacts`
- **Request Body**: JSON matching `ContactSchema`
- **Response**: Success or failure with HubSpot response details.

### 2. Create or Update Deal
**POST** `/deals`
- **Request Body**: JSON matching `DealSchema`
- **Response**: Success or failure with HubSpot response details.

### 3. Create Ticket
**POST** `/tickets`
- **Request Body**: JSON matching `TicketSchema` (must include `deal_ids`)
- **Response**: Success or failure with HubSpot response details.

### 4. Get CRM Objects
**GET** `/crm-objects?page={page}&size={size}&start_date={iso_datetime}`
- **Query Parameters**:
  - `page`: Pagination page number.
  - `size`: Number of items per page.
  - `start_date` (optional): ISO 8601 formatted date to filter tickets.
- **Response**: List of contacts, deals, and tickets.


---

## Authentication Details

This service uses OAuth2 Bearer Token authentication for HubSpot API calls. The token is managed via an `ITokenService` implementation.

- Access tokens are automatically retrieved from HubSpot and refreshed.
- Tokens must be stored securely (e.g., environment variable or secret manager).
- Each request to HubSpot is authenticated via the `Authorization: Bearer <token>` header.

---

## Environment Variable Configurations

| Variable               | Description                                                |
|------------------------|------------------------------------------------------------|
| `HUBSPOT_CLIENT_ID`    | Your HubSpot app's client ID.                              |
| `HUBSPOT_CLIENT_SECRET` | Your HubSpot app's client secret.                          |
| `HUBSPOT_REFRESH_TOKEN` | The refresh token to obtain new access tokens.            |

---

## Troubleshooting Steps

### Common Issues and Fixes

1. **Invalid or Expired Access Token**
   - Check your refresh token and client credentials.
   - Ensure the token service is correctly implemented and invoked.

2. **Network Errors or Timeouts**
   - Verify internet connectivity.
   - Check if HubSpot API is reachable (`https://status.hubspot.com`).

3. **Error Parsing JSON Responses**
   - Enable `DEBUG` log level to inspect raw responses.
   - Check HubSpot's API documentation for expected response formats.

4. **Missing Environment Variables**
   - Ensure all required variables are set in your `.env` file.
   - Use `print(os.environ)` to debug variable loading.

5. **Docker Build Failures**
   - Ensure Docker is installed and running.
   - Rebuild with `docker-compose build --no-cache`.

### Logging
Logs are output to stdout. Customize log configuration in `src/config/logger.py`.

---

## Contact
For questions or support, contact `davidnjoagwuani@gmail.com`


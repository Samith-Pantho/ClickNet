# ClickNet - Digital Banking Service

## Project Overview
A comprehensive **digital banking platform** that provides secure, convenient banking services through a modern web interface.
The application enables customers to manage accounts, perform transactions, and access banking features entirely online — while maintaining **robust security** and **compliance standards**.

---

## Core Services

### Authentication & Security Service
**Secure access management and identity verification**

#### Key Features
- **User Registration**
  Complete account creation with identity verification

- **Multi-Factor Login**
  OTP authentication via SMS and other secure channels

- **Password Management**
  - Secure password changes
  - Forgotten password recovery
  - User ID recovery options

- **Session Control**
  Secure login and logout mechanisms ensuring active session safety

---

### Banking Operations Service
**Comprehensive financial account management and transaction processing**

#### Account Management
- View all accounts with categorization
- Access detailed account information
- Check balances and available funds
- Review transaction limits

#### Financial Operations
- Transaction history with date-based filtering
- Bank statement generation (downloadable)
- Inter-account fund transfers
- Money deposit functionality

#### Customer Services
- Profile management with photo upload
- Customer activity tracking
- Complaint submission and tracking
- AI-powered chat support for instant assistance

---

### ClickKYC - KYC & Onboarding Service
**Streamlined customer verification and account opening**

#### Verification Process
- Mobile OTP verification
- Email OTP verification
- Multi-channel identity confirmation

#### Onboarding Workflow
- Product selection from catalog
- Branch selection
- Step-by-step digital application process
- Automated account creation upon verification
- Compliance reporting and audit trail

#### Product & Branch Information
- Comprehensive product lists with details
- Complete branch network directory

---

### Configuration Service
**Dynamic application settings and system customization**

#### Features
- **Application Settings**: Retrieve and manage configuration parameters dynamically
- **Branch Information**: Access centralized branch database and location details
- **Flexible Parameters**: Customizable settings for different use cases and organizations

---

### Location Services
**Branch and mapping integration**

#### Features
- **Waypoint Navigation**: Provides routes and directions to branches or ATMs
- **Branch Locator**: Geographic branch and ATM information based on user location

---

## Key User Benefits

### Customer Experience
- **24/7 Accessibility** — Banking services available anytime, anywhere
- **Self-Service Capabilities** — Perform most operations without visiting a branch
- **Intuitive Interface** — Easy navigation with a user-friendly design
- **Quick Onboarding** — Streamlined, paperless account creation process

---

### Security & Compliance
- **Multi-Layer Security** — CAPTCHA, OTP, and secure session management
- **Regulatory Compliance** — Adheres to banking and financial security standards
- **Data Protection** — Secure encryption and handling of financial information
- **Audit Trail** — Complete activity tracking for accountability

---

### Business Features
- **Complete Banking Suite** — Covers all essential banking operations
- **Customer Support** — Integrated complaint management and help systems
- **AI Assistance** — Smart chat-based support for real-time assistance
- **Mobile Optimization** — Accessible across all devices with responsive design

---

## Service Integration

The application seamlessly integrates these services to deliver a **unified digital banking experience**:

| Service | Function |
|----------|-----------|
| **Authentication** | Secures all user operations |
| **Banking Operations** | Handles financial transactions and account activities |
| **KYC & Onboarding** | Ensures compliance and smooth customer onboarding |
| **Configuration** | Provides business flexibility and dynamic control |
| **Location Services** | Enhances connectivity with physical branch networks |

---

## Architecture & File Structure

The project is organized into the following structure:

```
ClickNet/
├── docker-compose.yml          # Docker Compose configuration for all services
├── ngrok_kyc.yml              # Ngrok configuration for KYC tunneling
├── ngrok_net.yml              # Ngrok configuration for Net tunneling
├── README.md                  # Project documentation
├── BackEnd/                   # Backend services
│   ├── ClickKYCApi/          # KYC API service
│   │   ├── Dockerfile
│   │   ├── index.py
│   │   ├── requirements.txt
│   │   ├── Routes/            # API routes for KYC
│   │   ├── Services/          # Business logic services
│   │   ├── Schemas/           # Data validation schemas
│   │   ├── Models/            # Database models
│   │   ├── Config/            # Database configuration
│   │   ├── Cache/             # Caching layer
│   │   └── Templates/         # HTML templates
│   ├── ClickKYCWebhook/      # KYC Webhook service
│   ├── ClickNetApi/          # Main banking API service
│   ├── ClickNetWebhook/      # Banking Webhook service
│   └── Encrypt & Decrypt/    # Encryption utilities
├── FrontEnd/                  # Frontend applications
│   ├── clickkycweb/          # KYC web interface
│   │   ├── Dockerfile
│   │   ├── nginx.conf         # Nginx configuration for ClickKYC Web
│   │   ├── package.json
│   │   └── src/               # React source code
│   └── clicknetweb/          # Banking web interface
│       ├── Dockerfile
│       ├── nginx.conf         # Nginx configuration for ClickNet Web
│       ├── package.json
│       └── src/               # React source code
├── Database/                  # Database initialization scripts
│   ├── CBS/                   # Core Banking System schemas
│   ├── ClickKyc/             # KYC database schemas
│   └── ClickNet/             # Banking database schemas
├── logs/                      # Application logs
└── certs/                     # SSL certificates
```

---

## Installation & Usage

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ClickNet
   ```

2. **Configure Environment Variables:**
   Update the following in `docker-compose.yml`:
   - Database passwords: Replace `xxxxx` with secure passwords
   - Ngrok authtokens: Obtain from ngrok.com and replace `xxxxx`
   - Other secrets as needed

3. **Start the Application:**
   ```bash
   docker-compose up -d
   ```

4. **Access the Applications:**
   - ClickNet Web: http://localhost:3333
   - ClickKYC Web: http://localhost:2222
   - APIs: Internal network (configured in docker-compose)

### Development Setup
For development, you can run individual services:

```bash
# Run specific service
docker-compose up clicknetweb

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## API Documentation

### ClickNet API (Port 8443)
Main banking operations API with the following endpoints:

#### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /forgot-password` - Password recovery
- `POST /verify-otp` - OTP verification

#### Account Management
- `GET /accounts` - List user accounts
- `GET /accounts/{id}` - Account details
- `GET /balance` - Account balance

#### Transactions
- `GET /transactions` - Transaction history
- `POST /transfer` - Fund transfer
- `POST /deposit` - Money deposit
- `GET /statement` - Download statement

#### Profile & Support
- `GET /profile` - User profile
- `PUT /profile` - Update profile
- `POST /complaint` - Submit complaint
- `GET /complaints` - Complaint history

#### WebSocket
- `WS /initialize/{session_id}` - WebSocket connection for real-time updates

### ClickKYC API (Port 8444)
KYC and onboarding operations:

- `GET /products` - Product catalog
- `GET /branches` - Branch information
- `POST /kyc-session` - Initiate KYC session
- `POST /verify-identity` - Identity verification

### Webhook Services
- ClickNet Webhook (Port 9999): Handles banking webhooks
- ClickKYC Webhook (Port 8888): Handles KYC verification webhooks

---

## Configuration

### Database Configuration
The application uses MySQL databases:
- **CBS Database**: Core banking system data
- **ClickNet Database**: Banking application data
- **ClickKYC Database**: KYC and customer verification data

Database credentials are configured in `docker-compose.yml`:
```yaml
environment:
  - DB_CBS_USER=cbs_user
  - DB_CBS_PASSWORD=xxxxx  # Replace with secure password
  - DB_CLICKNET_USER=clicknet_user
  - DB_CLICKNET_PASSWORD=xxxxx  # Replace with secure password
  - DB_CLICKKYC_USER=clickkyc_user
  - DB_CLICKKYC_PASSWORD=xxxxx  # Replace with secure password
```

### 3rd Party Integrations

#### Didit (KYC Verification)
Didit is used for electronic Know Your Customer (eKYC) verification.

**Configuration:**
1. Sign up for Didit API at [didit.com](https://didit.com)
2. Obtain API credentials
3. Update the following in `Database/ClickKyc/ClickKYC_APP_SETTINGS_DATA.sql`:
   ```sql
   INSERT INTO APP_SETTINGS (`KEY`, VALUE) VALUES
   ('DIDIT_API_KEY', 'xxxxx'),  -- Your Didit API key
   ('DIDIT_WORKFLOW_ID', 'xxxxx'),  -- Your workflow ID
   ('DIDIT_CALLBACK_URL', 'https://your-domain.com/callback'),
   ('DIDIT_WEBHOOK_SECRET', 'xxxxx'),  -- Webhook secret
   ('DIDIT_WEBHOOK_KEY', 'xxxxx');  -- Webhook key
   ```
   **Important:** Note that `DIDIT_CALLBACK_URL` and your registered Didit webhook URL must point to your Ngrok tunnel address (e.g., `https://api.yourdomain.ngrok-free.app/didit-webhook`), not localhost or nginx.

**Usage:**
- The system creates Didit sessions for customer verification
- Webhooks handle verification results
- Supports face matching, ID verification, liveness detection

#### Google reCAPTCHA
Used for bot protection on forms.

**Configuration:**
1. Register at [Google reCAPTCHA](https://www.google.com/recaptcha/admin)
2. Get site key and secret key
3. Update in `Database/ClickNet/APP_SETTINGS_Insert_Data.sql`:
   ```sql
   INSERT INTO APP_SETTINGS (`KEY`, VALUE) VALUES
   ('GOOGLE_RECAPTCHA_SITE_KEY', 'xxxxx'),
   ('GOOGLE_RECAPTCHA_SECRET_KEY', 'xxxxx');
   ```

**API Endpoint:**
- `POST /VerifyCaptcha` - Verify CAPTCHA token

#### Stripe (Payment Processing)
Used for handling secure fund deposits and payments.

**Configuration:**
1. Register and obtain API keys at [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Update the following in `Database/ClickNet/APP_SETTINGS_Insert_Data.sql`:
   ```sql
   INSERT INTO APP_SETTINGS (`KEY`, VALUE) VALUES
   ('STRIPE_PUBLISHABLE_KEY', 'xxxxx'),
   ('STRIPE_SECRET_KEY', 'xxxxx'),
   ('STRIPE_WEBHOOK_SECRET', 'xxxxx'),
   ('STRIPE_CALLBACK_SUCCESS_URL', 'https://your-domain.com/addmoneycallback?data=_data_'),
   ('STRIPE_CALLBACK_CANCEL_URL', 'https://your-domain.com/addmoneycallback?data=_data_');
   ```
   **Important:** Your registered Stripe webhook endpoint in the Stripe Dashboard must be configured to point to your Ngrok tunnel address (e.g., `https://api.yourdomain.ngrok-free.app/stripe-webhook`), not `localhost` or `nginx`.

**Usage:**
- Use the Publishable Key in the frontend to securely tokenize payment methods.
- Use the Secret Key in the backend to create payment intents and confirm charges.
- The webhook secret is used by the API webhook service to verify incoming Stripe events asynchronously.

#### OpenAI (AI Assistant)
Used to provide intelligent, contextual AI chat support for customers.

**Configuration:**
1. Generate an API Key from the [OpenAI Platform](https://platform.openai.com/api-keys)
2. Update the following in `Database/ClickNet/APP_SETTINGS_Insert_Data.sql`:
   ```sql
   INSERT INTO APP_SETTINGS (`KEY`, VALUE) VALUES
   ('OPENAI_API_KEY', 'xxxxx');
   ```

**Usage:**
- The backend utilizes this key to process natural language queries from customers within the ClickNet helpdesk/chat interface.

#### WebSocket Configuration
WebSockets are configured to handle real-time notifications, session management, and live chat support dynamically.

**Requirements & Configuration:**
- Ensure the backend API is running. WebSocket endpoints bind to the main API server automatically.
- **Connection URL Format:** `ws://<api-host>:<api-port>/initialize/{session_id}`
  - Example Local: `ws://localhost:8443/initialize/session123`
  - From Frontend (`clicknetweb`): `ws://localhost:3333/ws` (proxied to API)

**Usage:**
- Upon successful login, the frontend establishes a WS connection using the user's session ID.
- The backend uses this dedicated channel to push real-time alerts (e.g., successful transactions, incoming transfers, KYC approval messages, or forced logouts for security).

#### Ngrok (Tunneling for Local Webhooks)
Ngrok provides secure tunnels for webhook callbacks during local development without a public domain.

**Configuration:**
1. Install ngrok CLI
2. Get authtoken from [ngrok.com](https://ngrok.com)
3. Update in `docker-compose.yml`:
   ```yaml
   environment:
     - NGROK_AUTHTOKEN=xxxxx  # Your ngrok authtoken
   ```
4. Configure tunnel URLs in `ngrok_net.yml` and `ngrok_kyc.yml`
5. Map these Tunnel URLs in your Stripe and Didit developer dashboards.

#### Nginx (Reverse Proxy & Static File Serving)
Nginx is heavily utilized within the project as a reverse proxy to route traffic between the frontend React applications and the backend FastAPI services, as well as serving the static frontend builds.

**Configuration:**
- **Frontend Serving:** Nginx handles serving the production builds (`ClickNetWeb` and `ClickKYCWeb`) dynamically within their respective Docker containers via `nginx.conf`.
- **API Routing:** Configured to map incoming frontend HTTP and WebSocket traffic securely to backend APIs (`clicknetweb -> api:8443` & `clickkycweb -> kyc:8444`).
- **Webhook Exposing:** When deploying to production or testing locally, 3rd-party webhook triggers (Stripe, Didit) must target the public Ngrok domain. Ngrok tunnels securely forward those incoming webhook events to the internal `clicknetwebhook` and `clickkycwebhook` services.

#### Twilio (SMS & WhatsApp Messaging)
Used for dispatching OTPs, temporary credentials, and important alerts via SMS or WhatsApp.

**Configuration:**
1. Register at [Twilio](https://www.twilio.com) and obtain an Account SID, Auth Token, and Sender Phone Number.
2. Update the following in `Database/ClickNet/APP_SETTINGS_Insert_Data.sql`:
   ```sql
   INSERT INTO APP_SETTINGS (`KEY`, VALUE) VALUES
   ('TWILIO_ACCOUNT_SID', 'xxxxx'),
   ('TWILIO_AUTH_TOKEN', 'xxxxx'),
   ('TWILIO_MOBILE_NUMBER', 'xxxxx');
   ```

**Usage:**
- The backend configures notifications to use SMS based on the `CREDENTIALS_SENDING_PROCESS` and `DEFAULT_AUTHENTICATION_TYPE` system settings.

#### Email Configuration (SMTP)
Used for executing secure email delivery of account statements, signup credentials, and password-reset links to customers.

**Configuration:**
1. Configure an App Password for your SMTP email provider (e.g., Gmail).
2. Update the following in `Database/ClickNet/APP_SETTINGS_Insert_Data.sql`:
   ```sql
   INSERT INTO APP_SETTINGS (`KEY`, VALUE) VALUES
   ('CLICKNET_SENDER_EMAIL', 'xxxxx@gmail.com'),
   ('CLICKNET_SENDER_EMAIL_PASS', 'xxxxx');
   ```

**Usage:**
- The system uses these credentials to dispatch HTML-formatted transactional emails asynchronously through the backend services.

#### Kafka (Message Queue)
Used as an event-driven message broker for asynchronous processing and inter-service communication.

**Configuration:**
- Bootstrap servers configure to `kafka:9092` automatically via `docker-compose.yml`.
- APIs rely on Kafka and Zookeeper being fully initialized.

**Usage:**
- **Notifications Channel**: Offloads resource-heavy operations like email, SMS, and WhatsApp dispatch to prevent blocking main API threads.
- **Audit Logging**: Asynchronously collects and stores customer activities and transactions to ensure strict compliance tracking without performance hits.
- **Real-Time Events**: Streams system-wide events (e.g., completed KYC verifications or successful Stripe deposits) to trigger subsequent automated workflows.

---

## Database Setup

The databases are automatically initialized using Docker volumes and SQL scripts:

1. **CBS Database**: `Database/CBS/` - Core banking tables and procedures
2. **ClickNet Database**: `Database/ClickNet/` - Application data and settings
3. **ClickKYC Database**: `Database/ClickKyc/` - KYC data and Didit integration

To reset databases:
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Recreate with fresh data
```

---

## Development

### Adding New Features
1. Create routes in appropriate `Routes/` directory
2. Implement business logic in `Services/`
3. Define data models in `Models/`
4. Add validation schemas in `Schemas/`
5. Update database scripts if needed

### Testing
- Run individual services with `docker-compose up <service>`
- Check logs with `docker-compose logs <service>`
- Use health check endpoints for service status

### Deployment
- Update environment variables for production
- Configure SSL certificates in `certs/`
- Set up proper domain names and reverse proxy

---

## Support

For issues or questions:
- Check application logs in `logs/` directory
- Review Docker container logs
- Ensure all environment variables are properly set
- Verify database connections and 3rd party API keys

---

## License

copyright © 2026 Samith Binda Pantho
---
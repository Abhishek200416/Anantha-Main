# 🍽️ Anantha Lakshmi - Traditional Food Delivery Platform

A full-stack e-commerce food ordering platform for traditional Indian foods with comprehensive features including user authentication, product catalog, shopping cart, order management, payment integration, and admin panel.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Support](#database-support)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Admin Panel](#admin-panel)
- [Testing Summary](#testing-summary)
- [Environment Variables](#environment-variables)

---

## ✨ Features

### Customer Features
- 🔐 **User Authentication** - Email/Password, Google OAuth, Phone OTP
- 🛍️ **Product Catalog** - Browse 58+ traditional food products across 7 categories
- 🛒 **Shopping Cart** - Add/remove items, manage quantities
- 📍 **Location Detection** - Auto-detect location and filter products by city
- 💳 **Razorpay Payment Integration** - Secure online payments (Test mode enabled)
- 📦 **Order Tracking** - Track orders by Order ID, Tracking Code, Phone, or Email
- 📧 **Email Notifications** - Order confirmation and status update emails
- 🌐 **Multi-language Support** - English and Telugu
- 📱 **Mobile Responsive** - Works seamlessly on all devices
- 🔄 **Reorder Functionality** - Quick reorder from previous orders

### Admin Features
- 📊 **Dashboard** - Analytics, sales reports, order statistics
- 📦 **Order Management** - View, update, and manage all orders
- 🍕 **Product Management** - CRUD operations for products
- 💰 **Discount Management** - Set product discounts with expiry dates
- 📍 **Location Management** - Manage delivery cities and charges (431 cities)
- 🎉 **Festival Special** - Feature special products
- 🐛 **Bug Reports** - Customer issue tracking
- ⚙️ **Settings** - Payment settings, Razorpay configuration

---

## 🛠️ Tech Stack

### Frontend
- **React** 18.x
- **React Router** - Navigation
- **Context API** - State management
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client

### Backend
- **FastAPI** - Python web framework
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **PyJWT** - Authentication
- **Razorpay** - Payment gateway
- **Gmail SMTP** - Email notifications
- **Bcrypt** - Password hashing

### Database
- **MongoDB** (Primary) - NoSQL document database
- **PostgreSQL** (Optional) - Relational database support

### DevOps
- **Supervisor** - Process management
- **Nginx** - Reverse proxy (production)
- **Docker** - Containerization ready

---

## 📁 Project Structure

```
/app/
├── backend/
│   ├── database/
│   │   ├── models/           # Pydantic models organized by category
│   │   │   ├── __init__.py
│   │   │   ├── user_models.py
│   │   │   ├── product_models.py
│   │   │   ├── order_models.py
│   │   │   ├── location_models.py
│   │   │   └── admin_models.py
│   │   ├── connection_mongodb.py    # MongoDB connection manager
│   │   ├── connection_postgresql.py # PostgreSQL connection manager
│   │   └── __init__.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── helpers.py        # Utility functions
│   │   └── admin_manager.py  # Admin auto-creation
│   ├── server.py             # Main FastAPI application
│   ├── auth.py               # Authentication utilities
│   ├── gmail_service.py      # Email notification service
│   ├── email_service.py      # Alternative email service
│   ├── cities_data.py        # City and location data
│   ├── distance_calculator.py
│   ├── requirements.txt
│   └── .env                  # Environment configuration
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── contexts/         # React contexts (Cart, Admin, Language)
│   │   ├── pages/            # Page components
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
├── test_result.md            # Testing documentation and history
└── README.md                 # This file
```

---

## 🗄️ Database Support

### MongoDB (Primary - Currently Active)

The application primarily uses MongoDB for data storage.

**Collections:**
- `users` - User accounts and authentication
- `products` - Product catalog (58 items)
- `orders` - Customer orders
- `locations` - Delivery cities (431 cities: 217 AP + 214 Telangana)
- `states` - State information
- `admin_profiles` - Admin credentials
- `payment_settings` - Payment configuration
- `razorpay_settings` - Razorpay credentials
- `whatsapp_numbers` - WhatsApp contact numbers
- `bug_reports` - Customer issue reports
- `customer_data` - Customer information cache

### PostgreSQL (Optional)

PostgreSQL support is available as an alternative database. To use PostgreSQL:

1. Set up PostgreSQL credentials in `.env`
2. The application will auto-create all necessary tables
3. Tables mirror the MongoDB schema with proper relationships

---

## 🚀 Installation

### Prerequisites
- **Node.js** 16+ and Yarn
- **Python** 3.8+
- **MongoDB** 4.4+
- **PostgreSQL** 13+ (optional)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd app
```

### Step 2: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies
```bash
cd ../frontend
yarn install
```

---

## ⚙️ Configuration

### Environment Variables

Create `/app/backend/.env` with the following configuration:

```env
# ============= DATABASE CONFIGURATION =============
# MongoDB Configuration (Primary Database - Currently Active)
MONGO_URL="mongodb://localhost:27017"
DB_NAME="anantha_lakshmi_db"

# PostgreSQL Configuration (Alternative Database - Optional)
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="your_password"
POSTGRES_DB="anantha_lakshmi_db"

# ============= APPLICATION CONFIGURATION =============
CORS_ORIGINS="*"
JWT_SECRET="your-secret-key-change-in-production"

# ============= ADMIN CREDENTIALS =============
# Admin credentials are automatically created/updated on server startup
ADMIN_EMAIL="admin@ananthalakshmi.com"
ADMIN_PASSWORD="admin123"

# ============= PAYMENT GATEWAY =============
RAZORPAY_KEY_ID="rzp_test_Renc645PexAmXU"
RAZORPAY_KEY_SECRET="ReA5MNv3beAt068So4iYNq8s"

# ============= EMAIL CONFIGURATION =============
GMAIL_EMAIL="contact.ananthahomefoods@gmail.com"
GMAIL_APP_PASSWORD="your_app_password"

# SendGrid (Alternative - Optional)
SENDGRID_API_KEY=""
FROM_EMAIL="contact.ananthahomefoods@gmail.com"
```

### Frontend Configuration

The frontend uses environment variables from `/app/frontend/.env`:

```env
REACT_APP_BACKEND_URL=<automatically configured>
```

---

## 🏃 Running the Application

### Development Mode

#### Start Backend
```bash
cd /app/backend
sudo supervisorctl restart backend
```

Backend runs on: `http://localhost:8001`

#### Start Frontend
```bash
cd /app/frontend
sudo supervisorctl restart frontend
```

Frontend runs on: `http://localhost:3000`

### Service Management

```bash
# Restart all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8001/api`
- Production: `<your-domain>/api`

### Authentication APIs

#### Admin Login
```http
POST /api/auth/admin-login
Content-Type: application/json

{
  "email": "admin@ananthalakshmi.com",
  "password": "admin123"
}
```

#### User Registration
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "phone": "9876543210"
}
```

#### User Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Product APIs

#### Get All Products
```http
GET /api/products
```

#### Get Product by ID
```http
GET /api/products/{product_id}
```

#### Create Product (Admin Only)
```http
POST /api/products
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "id": "product_id",
  "name": "Product Name",
  "category": "Category",
  "description": "Description",
  "image": "image_url",
  "prices": [
    {"weight": "250g", "price": 250},
    {"weight": "500g", "price": 450},
    {"weight": "1kg", "price": 850}
  ]
}
```

### Order APIs

#### Create Order
```http
POST /api/orders
Content-Type: application/json

{
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "whatsapp_number": "9876543210",
  "doorNo": "12-34",
  "street": "Main Street",
  "city": "Guntur",
  "state": "Andhra Pradesh",
  "pincode": "522001",
  "items": [...],
  "subtotal": 1000,
  "delivery_charge": 49,
  "total": 1049,
  "payment_method": "razorpay"
}
```

#### Track Order
```http
GET /api/orders/track/{identifier}
```
Where `identifier` can be:
- Order ID (e.g., `AL20251216001`)
- Tracking Code (e.g., `ABC123XYZ`)
- Phone Number (e.g., `9876543210`)
- Email (e.g., `john@example.com`)

### Payment APIs

#### Create Razorpay Order
```http
POST /api/payment/create-razorpay-order
Content-Type: application/json

{
  "amount": 1049,
  "order_id": "AL20251216001"
}
```

#### Verify Payment
```http
POST /api/payment/verify-razorpay-payment
Content-Type: application/json

{
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "razorpay_signature": "signature_xxx",
  "order_id": "AL20251216001"
}
```

### Location APIs

#### Get All Locations
```http
GET /api/locations
```

#### Get States
```http
GET /api/states
```

---

## 👨‍💼 Admin Panel

Access the admin panel at: `/admin`

### Admin Credentials
- **Email**: Configured in `.env` (default: `admin@ananthalakshmi.com`)
- **Password**: Configured in `.env` (default: `admin123`)

**Note**: Admin credentials are automatically created/updated from `.env` file on server startup.

### Admin Features
1. **Dashboard** - Overview of orders, sales, and analytics
2. **Orders** - Manage all customer orders
3. **Products** - Add, edit, delete products
4. **Discounts** - Manage product discounts
5. **Inventory** - Track and update stock
6. **Locations** - Manage delivery cities and charges
7. **Settings** - Configure payment settings
8. **Bug Reports** - View customer issues

---

## 🧪 Testing Summary

### Backend Testing Status: ✅ All Tests Passed

**Tested Components:**
- ✅ Admin Authentication (JWT Token) - WORKING
- ✅ User Authentication - WORKING
- ✅ Product Management APIs - WORKING (58 products)
- ✅ Order Management APIs - WORKING
- ✅ Order Tracking (Multiple formats) - WORKING
- ✅ Razorpay Payment Integration - WORKING
- ✅ Email Notifications - WORKING
- ✅ Location Management - WORKING (431 cities)
- ✅ Admin Payment Settings - WORKING
- ✅ Order Analytics - WORKING
- ✅ Image Upload - WORKING
- ✅ Inventory Management - WORKING

### Frontend Testing Status: ✅ Functional

**Tested Components:**
- ✅ Home Page with Product Catalog
- ✅ Shopping Cart Functionality
- ✅ Checkout Process
- ✅ Order Tracking
- ✅ Admin Panel
- ✅ Location Detection
- ✅ Payment Integration (Razorpay Modal)
- ✅ Language Switching (English/Telugu)
- ✅ Mobile Responsiveness

### Database Status: ✅ Operational

**MongoDB Collections:**
- ✅ Products: 58 items across 7 categories
- ✅ Locations: 431 cities (217 AP + 214 Telangana)
- ✅ Admin: Auto-created from .env
- ✅ All collections properly seeded

---

## 🔧 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `anantha_lakshmi_db` |
| `ADMIN_EMAIL` | Admin email (auto-created) | `admin@ananthalakshmi.com` |
| `ADMIN_PASSWORD` | Admin password (auto-created) | `admin123` |
| `JWT_SECRET` | Secret key for JWT tokens | `your-secret-key` |
| `RAZORPAY_KEY_ID` | Razorpay test key ID | `rzp_test_xxx` |
| `RAZORPAY_KEY_SECRET` | Razorpay test secret | `xxx` |
| `GMAIL_EMAIL` | Gmail for sending emails | `your-email@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail app password | `xxxx xxxx xxxx xxxx` |

### Optional Variables (PostgreSQL)

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | - |
| `POSTGRES_DB` | PostgreSQL database name | `anantha_lakshmi_db` |

---

## 📦 Product Categories

1. **Laddus & Chikkis** (8 products)
2. **Sweets** (10 products)
3. **Hot Items** (10 products)
4. **Snacks** (3 products)
5. **Veg Pickles** (9 products)
6. **Powders** (12 products)
7. **Spices** (4 products)

---

## 🌍 Delivery Coverage

**Total Cities**: 431
- **Andhra Pradesh**: 217 cities
- **Telangana**: 214 cities

Delivery charges vary by city (₹49 - ₹149). Free delivery threshold can be configured per city.

---

## 🔐 Security Features

- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ Protected admin routes
- ✅ CORS configuration
- ✅ Environment variable protection
- ✅ Razorpay signature verification
- ✅ Input validation with Pydantic

---

## 📞 Support

For issues or questions:
- Email: contact.ananthahomefoods@gmail.com
- Bug Report: Use the bug report feature in the application

---

## 📝 License

This project is proprietary software for Anantha Lakshmi Traditional Foods.

---

## 🎉 Recent Updates

### Latest Session (December 2024)
- ✅ Reorganized database models into separate modules
- ✅ Added PostgreSQL support (optional)
- ✅ Admin auto-creation from .env on startup
- ✅ Cleaned up test files and unnecessary code
- ✅ Updated .gitignore for better repository management
- ✅ Created comprehensive README documentation
- ✅ Improved code organization and structure

### Previous Session
- ✅ Telugu language support for products
- ✅ Order confirmation and cancellation emails
- ✅ Admin panel consistency improvements
- ✅ Razorpay payment integration
- ✅ City matching bug fixes
- ✅ Product database reseeding

---

**Built with ❤️ for Anantha Lakshmi Traditional Foods**
# Anantha-Main
# Anantha-Main

# Role-Based Access Control Implementation

This document describes the role-based access control (RBAC) system that has been implemented for the Procurement Transparency Platform.

## Overview

The application has been converted from a multi-dashboard system where all portals were accessible simultaneously to a role-based access system with three distinct portals:

1. **Government Portal** - Single account with access code authentication
2. **Vendor Portal** - Multiple accounts with vendor ID and password authentication
3. **Public Portal** - No authentication required

## Architecture

### Backend Changes

#### 1. Authentication Models (`backend/app/db/models.py`)
- **GovernmentAccount**: Stores the single government account with hashed access code
- **Vendor**: Updated to include `password_hash` and `vendor_id` fields for authentication

#### 2. Authentication Service (`backend/app/services/auth.py`)
- JWT token generation and verification
- Password hashing using bcrypt
- Role-based access control dependencies
- Token expiration (24 hours)

#### 3. Authentication Routes (`backend/app/routes/auth.py`)
- `POST /auth/government/login` - Government login with access code
- `POST /auth/vendor/login` - Vendor login with vendor ID and password
- `POST /auth/vendor/register` - Vendor registration with authentication
- `GET /auth/me` - Get current authenticated user info
- `POST /auth/logout` - Logout endpoint

#### 4. Protected Routes
All existing routes have been updated to require authentication:
- **Government routes** (`/gov/*`): Require `government` role
- **Vendor routes** (`/vendor/*`): Require `vendor` role
- **Public routes** (`/public/*`): No authentication required

### Frontend Changes

#### 1. Role Selection Screen (`frontend/src/pages/RoleSelection.jsx`)
- Entry point for the application
- Three buttons: Government, Vendor, Public
- No other content until role is selected

#### 2. Login Components
- **GovernmentLogin** (`frontend/src/pages/GovernmentLogin.jsx`): Access code input
- **VendorLogin** (`frontend/src/pages/VendorLogin.jsx`): Vendor ID and password
- **VendorRegister** (`frontend/src/pages/VendorRegister.jsx`): New vendor registration

#### 3. Authentication Context (`frontend/src/contexts/AuthContext.jsx`)
- Manages user authentication state
- Handles login, logout, and registration
- Persists session in localStorage
- Provides authentication state to all components

#### 4. Protected Routes (`frontend/src/components/ProtectedRoute.jsx`)
- Wraps dashboard components
- Redirects unauthenticated users to login
- Redirects users to correct dashboard based on role

#### 5. Updated Dashboards
- **GovDashboard**: Added logout button, role-specific header
- **VendorDashboard**: Removed registration flow (moved to separate page), added logout
- **PublicDashboard**: Added "Back to Role Selection" button

#### 6. API Service Updates (`frontend/src/services/api.js`)
- Automatic token injection in request headers
- 401 error handling (auto-logout and redirect)
- New authentication API endpoints

## Setup Instructions

### 1. Initialize Government Account

Before the government portal can be used, you must initialize the government account with an access code:

```bash
docker compose exec backend python -m app.scripts.init_government_account admin123

```

Or using environment variable:
```bash
GOVERNMENT_ACCESS_CODE=your_code python -m app.scripts.init_government_account
```

**Important**: Keep the access code secure. It cannot be recovered if lost.

### 2. Database Migration

The new models will be created automatically when the application starts. If you need to manually create them:

```bash
cd backend
python -c "from app.db.session import engine, Base; from app.db.models import *; Base.metadata.create_all(bind=engine)"
```

### 3. Start the Application

The application works the same way as before:

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

## User Flows

### Government User Flow
1. User opens application → Role Selection screen
2. Clicks "Government" → Government Login screen
3. Enters access code → Redirected to Government Dashboard
4. Can create tenders, view bids, award contracts
5. Logout → Returns to Role Selection screen

### Vendor User Flow
1. User opens application → Role Selection screen
2. Clicks "Vendor" → Vendor Login screen
3. Option A: Has account → Enters Vendor ID and password → Vendor Dashboard
4. Option B: New vendor → Clicks "Register" → Registration form → Auto-login → Vendor Dashboard
5. Can browse tenders, submit bids, view bid history
6. Logout → Returns to Role Selection screen

### Public User Flow
1. User opens application → Role Selection screen
2. Clicks "Public" → Immediately redirected to Public Dashboard
3. Can view awarded tenders, transparency data, submit ratings
4. "Back to Role Selection" button available

## Security Features

1. **Password Hashing**: All passwords and access codes are hashed using bcrypt
2. **JWT Tokens**: Secure token-based authentication with 24-hour expiration
3. **Role-Based Access**: Backend routes verify user role before allowing access
4. **Session Persistence**: Tokens stored in localStorage, validated on page refresh
5. **Automatic Logout**: 401 errors trigger automatic logout and redirect

## API Endpoints

### Authentication
- `POST /auth/government/login` - Government login
- `POST /auth/vendor/login` - Vendor login
- `POST /auth/vendor/register` - Vendor registration
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Protected Endpoints
All existing endpoints now require authentication:
- Government endpoints require `Authorization: Bearer <token>` header with government role
- Vendor endpoints require `Authorization: Bearer <token>` header with vendor role
- Public endpoints remain open (no authentication required)

## Migration Notes

### Existing Vendors
Existing vendors in the database will need to:
1. Register through the new registration flow to set up authentication
2. Or have their accounts manually updated with password hashes

### Backward Compatibility
- The old `/vendor/register` endpoint still exists but only creates vendor records without authentication
- New vendors should use `/auth/vendor/register` for full authentication setup

## Testing

### Test Government Login
1. Initialize government account: `python -m app.scripts.init_government_account test123`
2. Open application → Click Government → Enter "test123"
3. Should redirect to Government Dashboard

### Test Vendor Registration
1. Open application → Click Vendor → Click "Register"
2. Fill in registration form with vendor ID, password, and company details
3. Should auto-login and redirect to Vendor Dashboard

### Test Public Access
1. Open application → Click Public
2. Should immediately show Public Dashboard without any login

## Troubleshooting

### "Government account not configured"
- Run the initialization script: `python -m app.scripts.init_government_account <code>`

### "Invalid authentication credentials"
- Token may have expired (24 hours)
- User needs to log in again

### "Access denied" errors
- User is trying to access a route they don't have permission for
- Check that the user's role matches the required role for the route

### Frontend not redirecting correctly
- Clear localStorage: `localStorage.clear()`
- Refresh the page

## Future Enhancements

Potential improvements:
1. Token refresh mechanism
2. Remember me functionality
3. Password reset for vendors
4. Access code reset for government (with admin approval)
5. Session timeout warnings
6. Multi-factor authentication





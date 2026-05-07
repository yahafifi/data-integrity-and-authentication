# Flask Security Lab: OAuth + JWT + Password Policy + RBAC + SQL Server

This is a teaching-ready Flask app for Data Integrity and Authentication students.

## Concepts Covered

- Manual registration
- Password policy validation
- Password hashing using bcrypt
- Google OAuth login
- JWT token generation
- RBAC authorization
- SQL Server database storage
- Protected API testing using Postman

---

## 1. Create SQL Server Database

Open SQL Server Management Studio and run:

```sql
create database SecurityLabDB;
```

The app automatically creates the `users` table when it starts.

---

## 2. Install ODBC Driver

Install Microsoft ODBC Driver 17 or 18 for SQL Server.

If you use Driver 18, update `.env`:

```env
DATABASE_URL=mssql+pyodbc://@localhost/SecurityLabDB?driver=ODBC+Driver+18+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes
```

---

## 3. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Update:

```env
FLASK_SECRET_KEY=any-random-secret
JWT_SECRET_KEY=any-random-jwt-secret
DATABASE_URL=mssql+pyodbc://@localhost/SecurityLabDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OAUTHLIB_INSECURE_TRANSPORT=1
```

---

## 5. Google OAuth Setup

In Google Cloud Console:

1. Create a project
2. Go to APIs & Services
3. Configure OAuth Consent Screen
4. Create OAuth Client ID
5. Choose Web Application
6. Add redirect URI:

```text
http://127.0.0.1:5000/auth/google/callback
```

Also add:

```text
http://localhost:5000/auth/google/callback
```

---

## 6. Run the App

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 7. Test Password Policy

Valid example:

```text
Yahia@2026
```

Invalid examples:

```text
12345678
password
Yahia2026
```

---

## 8. Test JWT Protected APIs in Postman

After login, copy the JWT token from the dashboard.

### Profile API

```http
GET http://127.0.0.1:5000/api/profile
Authorization: Bearer YOUR_TOKEN_HERE
```

### Admin API

```http
GET http://127.0.0.1:5000/api/admin
Authorization: Bearer YOUR_TOKEN_HERE
```

If the role is not admin, the API returns 403 Forbidden.

---

## 9. Teaching Notes

### Important Security Note

The registration page allows choosing `admin` role only for teaching/demo purposes.

In real systems:

- Users must not choose their own role
- Admin role should be assigned only by an existing administrator
- OAuth redirect URIs must be restricted
- Tokens must be stored securely
- HTTPS is required in production

---

## 10. Useful Classroom Experiments

Ask students to:

1. Register with a weak password and observe rejection
2. Register with a strong password
3. Inspect the database and see that password is hashed
4. Login and copy JWT token
5. Decode the JWT using jwt.io
6. Modify the JWT payload and test API rejection
7. Login using Google OAuth
8. Compare local login vs OAuth login
9. Test `/api/admin` with student and admin users

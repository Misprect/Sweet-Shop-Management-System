# Sweet Shop Management System (Frontend)

This repository contains the complete frontend architecture for a modern Sweet Shop Management System, built using **React** and **TypeScript** with **Bootstrap** for styling. The application is designed to support both customer e-commerce operations and comprehensive administration.

## Features

The system is fully structured with protected routes for user authentication and authorization.

### Customer / Standard User Features

- **Authentication:** Secure Login and Registration.
- **Product Browsing:** View available sweets (`Dashboard.tsx`).
- **Cart Management:** Add, remove, and update quantities of sweets in the shopping cart (`CartSummary.tsx`).
- **Order Placement:** Place a final order via a secure API call.

### Administrator Features

- **Protected Routes:** All admin panels are guarded by `AdminRoute` based on the user's `is_admin` status.
- **Product CRUD:** Create, Read, Update, and Delete sweets (`SweetListAdmin.tsx`, `SweetForm.tsx`).
- **Order Management:** View all customer orders and update their statuses (Pending, Processing, Completed) (`OrderListAdmin.tsx`).
- **User Management:** View all registered users and toggle their admin privileges (Promote/Demote) (`UserListAdmin.tsx`).

## Architecture and Technology Stack

| Category       | Technology / Component                | Details                                            |
| :------------- | :------------------------------------ | :------------------------------------------------- |
| **Framework**  | React v18+                            | Component-based UI development.                    |
| **Language**   | TypeScript                            | Strong typing for reliability and scalability.     |
| **Styling**    | Bootstrap 5                           | Responsive design and utility classes.             |
| **State/Auth** | React Context API (`AuthContext.tsx`) | Global state management for user authentication.   |
| **Routing**    | React Router DOM v6                   | Protected routes (`PrivateRoute`, `AdminRoute`).   |
| **API**        | Axios (`api/index.ts`)                | HTTP client configured for authenticated requests. |

## Project Structure

The structure is organized to cleanly separate application logic, presentation components, and management panels.

```
sweet-shop-frontend/
├── src/
│   ├── api/
│   │   └── index.ts          # Axios configuration for authenticated requests
│   ├── components/
│   │   ├── Admin/
│   │   │   ├── OrderListAdmin.tsx   # View/Update customer orders
│   │   │   ├── SweetForm.tsx        # Create & Edit Sweet form (reusable)
│   │   │   ├── SweetListAdmin.tsx   # Admin product list view
│   │   │   └── UserListAdmin.tsx    # Manage user admin status
│   │   ├── Auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── Layout/
│   │   │   └── Navbar.tsx           # Dynamic navigation with admin links
│   │   ├── CartSummary.tsx          # Cart display, total, and checkout logic
│   │   ├── Dashboard.tsx            # Main customer product browsing view
│   │   └── SweetCard.tsx            # Individual sweet item component
│   ├── context/
│   │   └── AuthContext.tsx          # Authentication Context Provider
│   ├── hooks/
│   │   └── useAuth.ts               # Custom hook for auth state
│   └── App.tsx                      # Main router setup (defines all protected routes)
└── ...
```

## Getting Started

### Prerequisites

- Node.js (LTS recommended)
- npm or yarn
- A running backend API (expected to serve endpoints like `/api/sweets/`, `/api/orders/`, `/api/auth/`, etc.)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Misprect/Sweet-Shop-Management-System.git
    cd sweet-shop-frontend
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    # or
    yarn install
    ```

3.  **Configure API Base URL:**
    Ensure your `src/api/index.ts` file points to your running backend (e.g., `http://localhost:8000/api/`).

### Running the Application

Start the development server:

```bash
npm start
# or
yarn start
```

The application should open in your browser at `http://localhost:3000`.

## Authors

This project was developed through a collaboration between the project owner and an AI assistant.

- **Project Owner:** [Misprect]
- **Co-Author / AI Assistant:** Gemini (Google)

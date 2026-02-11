# Frontend Application

This repository contains the frontend application of the project.

The system is developed following an MVP strategy,
with core architecture and data flow defined upfront
to support scalability and future iteration.

---

## Overview

- React-based frontend application
- Communicates with a Flask RESTful backend
- Supports authentication and protected routes
- UI built with reusable components and layouts

---

## Tech Stack

- React 19
- TypeScript
- Vite
- React Router v6
- Axios
- Ant Design (antd)

---

## Project Structure

```text
src/
├── assets/        # Images / SVGs
├── components/    # Reusable UI and layout components
├── layouts/       # Page layout templates
├── pages/         # Page-level components
├── routers/       # Route definitions
├── services/      # API abstraction layer
├── styles/        # Global styles
├── utils/         # Utility functions
├── App.tsx        # Router mounting
└── main.tsx       # Application entry
```

## How to run
```terminal
cd frontend
npm install
npm run dev
```
The application will start in development mode using Vite.

## Architecture & Design
Detailed frontend architecture, component responsibilities,
UI flow, and API mapping are documented here:
[Frontend Technical Design](https://www.notion.so/Frontend-Technical-Design-Document-2fe327f3e207803bbf8cc28f2ef51094?source=copy_link)
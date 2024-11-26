
# Ticketing System
This project is a full-stack ticket booking system that allows users to book tickets in real-time, view their tickets, and update their bookings. The system supports real-time updates and notifications for ticket status and availability. The frontend uses React with Server-Side Rendering (SSR), while the backend is powered by Django, Django Channels, Redis, and PostgreSQL.


## Features

- Real-Time Ticket Booking: Users can book tickets in real-time, and the system instantly updates availability.
- View and Manage Tickets: Users can view their booked tickets and make changes (e.g., cancel or update).
- Real-Time Notifications: Users receive real-time updates regarding the status of their bookings via WebSockets.
- User Authentication: Secure user registration and login process.
- Session Management: Sessions are managed using Django's built-in session handling.
- Server-Side Rendering (SSR): React components are server-rendered for improved SEO and faster page loads.



## Tech Stack

**Frontend** React, HTML, CSS, JavaScript, Server-Side Rendering (SSR)

**Backend** Django, Django Channels

**Real-Time Communication** Redis, WebSockets (via Django Channels)

**Database** PostgreSQL

**Session Management** Django sessions

**Authentication** Django's built-in authentication system

**Real-Time Communication Layer** Redis as the channel layer for WebSocket communication


## Run Locally

Clone the project

```bash
  git clone https://github.com/Deadlover/Ticket-System-website
```

Go to the project directory

```bash
  cd foldername
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  python manage.py runserver
```


## Screenshots

## Login
![Login Screenshot](app/static/image/Screenshot%202024-11-22%20234124.png)

## Home
![Home Screenshot](app/static/image/Screenshot%202024-11-22%20234142.png)


## Movie Page
![MoviePage Screenshot](app/static/image/Screenshot%202024-11-22%20234212.png)


## Hall Page
![HallPage Screenshot](app/static/image/Screenshot%202024-11-22%20235531.png)

## Ticket Page
![TicketPage Screenshot](app/static/image/Screenshot%202024-11-22%20235550.png)


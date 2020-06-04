Search Portal Single Page Application
=====================================

A frontend build in Vue that provides a search bar, filters and viewing results.
As well as a way for users to organise themselves in communities.


Installation
------------

Installation of the frontend is a lot more straightforward than the other components.
From the ``portal`` directory run:

```bash
npm install
```


Getting started
---------------

You can run the frontend with its own server.

```bash
npm run serve
```


#### Available apps

If you run the frontend development server it becomes available under:

```bash
http://localhost:8080/
```


#### Logging in locally

On the servers the login works through SURFConext.
It's a bit of a hassle to make that work locally.
So we've opted for a way to work around SURFConext when logging in during development.

Simply login to the Django admin of the ``service``.
Once logged in clicking the frontend login button.
This will fetch an API token in development mode and "log you in".
From there on out there is no difference between the remote and local login.

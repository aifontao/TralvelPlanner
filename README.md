# Travel Planner

#### Video Demo: https://youtu.be/7XdfjiJlPMw

#### Description:
# TravelPlanner

TravelPlanner is a full-stack web application I created as my final project for CS50x. It helps users **organize, plan, and reflect** on their past, current, and future travels. This project was built using **Python with Flask**, along with **HTML, CSS, JavaScript**, and **SQLite** for persistent data storage.

Users can register and log in to access their personal travel dashboard. From there, they can add new trips with details such as **country, city, and trip type** (e.g., holiday, work), and assign a **status** to each trip: *wishlist*, *planning*, *scheduled*, *ongoing*, or *completed*. Users can **edit** or **delete** any trip at any time.

A key feature of TravelPlanner is the ability to add **travel buddies** to each trip, including their name and relationship (e.g., friend, family, coworker). These can also be edited or removed as needed. For completed trips, users can **rate the experience** and leave **comments or reflections**, making the app useful not only for planning but also for journaling and looking back on travel memories.

The site includes a **secure login system**, password hashing, and session management. Users can also update their password from within their dashboard.

Throughout development, I focused on creating a **clean and user-friendly design**, following responsive layout principles and ensuring that the app works smoothly across different devices.

### Technologies Used

- Python (Flask)
- HTML, CSS, JavaScript
- SQLite (relational database)
- Jinja2 (Flask templating)
- CS50 Library & helpers

### Challenges Faced

Some challenges I encountered included managing relational data between trips and their buddies, implementing update/delete operations without breaking relationships, and validating user input securely across multiple forms.

### Planned Future Features

- Add the ability to track specific **places to visit**, **foods to try**, and **activities**
- Include **budget planning and expense tracking**
- Allow users to **upload photos** for each trip
- Integrate **APIs** (e.g., weather, maps, flights)
- View trips on an interactive map

This project allowed me to apply many of the programming and web development concepts covered in CS50, from **SQL and data modeling**, to **routing and session management** in Flask. It also gave me experience in debugging, feature design, and front-end development.

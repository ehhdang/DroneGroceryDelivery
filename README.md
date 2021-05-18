# Drone Grocery Delivery
Author: Emma Dang

Date: April 25th, 2021

Drone Grocery Delivery is a web application for
online grocery shopping via drones. It provides
an interface for 4 types of users - admin, chain
manager, drone technicians, and customers.
* a user can register either as an employee 
(manager or drone technician) or a customer.
* an admin can create grocery chains, stores,
drones, items, and view customers
* a chain manager can create chain items, view 
drone technicians, view drones, and manage stores
* a drone technician can view store orders,
assign his drones to an order, view order details,
and track his assigned drones.
* a customer can view and shop store items,
review and place an order, view order history,
and update his or her payment method

The Drone Delivery App uses Flask
framework, HTML, CSS, Bootstrap, and MySQL as a 
persistent database storage.

## Install
##### MySQL
Download and install MySQL from https://dev.mysql.com/downloads/ 

##### MySQL Workbench
Download and install MySQL Workbench from https://www.mysql.com/products/workbench/ 

##### Python 3.6+ and PIP
Download and install Python from https://www.python.org/

#### Flask
```
pip install Flask
```
#### mysql-client
Follow the instruction [here](https://pypi.org/project/mysqlclient/)
to install mysql-client on your machine

#### flask-mysqldb
```
pip install flask-mysqldb
```

## Run App
#### Initalize the database
Open MySQL Workbench. Navigate to the project folder DroneDeliveryApp/db and open
the grocery_drone_delivery.sql and phase4_shell.sql

In the grocery_drone_delivery.sql script, hit the lightning bolt button to execute the script
and initialize the database

In the phase4_shell.sql, hit the lightning bolt button to create all the procedures for the application

Open a new script and execute the following command to hash all the users' passwords
```
call hash_passwords;
```

#### Run the application
In your terminal, navigate to the project folder,
then execute the command above to launch the web ap
```
python app.py
```
Go to http://127.0.0.1:5000/ in your browser
to see the app in action.



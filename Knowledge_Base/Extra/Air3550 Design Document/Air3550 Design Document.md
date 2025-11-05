**EECS 3550**

**Software Engineering**

**Spring Semester 2023**

**Air3550 Project**



**Design Document**
**\

**\


**Report Author: Hoang Nhat Duy Le**

`			`**Joshua Davenport**

`			`**Sanskar Lamsal**

**Section: 001**







**Date due        	3/19/2023**

**Date submitted        	3/19/2023**
**\


**Grade         	     \_\_\_/100**












**Table of Contents**

**I.** 	Introduction...………….………………….       	3

**II.**       System Architecture...…...………………       4

**III.**    Frontend Architecture…..………………..       6

**IV.**    Backend Architecture…..………………..       10

**V.**    Database Architecture....………………...       12

**VI.**    Map Structure & Flight Path……...……..       13










1. **Introduction**

**1.1 Project Overview**

This project is Air3550 - a replication of a complete reservation system for a new airline. It will include all necessary functions such as a booking system, fight management, and various roles to define how you can interact with the system. For this deliverable, we are constructing a requirement document that consists of an interpretation of each requirement and provides an understanding of potential use cases.

**1.2 Scope**

This project designs and implements a fully functional Airline booking system. It is implemented using a well-designed relational database, using .Net framework and SQL Lite to store all air flight information and can be fetched easily through controllers. A friendly user interface is provided so that various combinations of search criteria can be fetched from the user and generates corresponding database search statements. It also supports a registration and login system where user can provide their username and password to authenticate and perform various operations.

**1.3 Purpose**

The design document will provide a general view of the project architecture (for the frontend and backend) and a comprehensive illustration of the database schema. The purpose of this document is to demonstrate the design of the project according to the requirement and help the team to visualize how to set up the structure of the project. In this document, we will go through the main architecture of the back-end side and the front-end side.

Team Members:

- Hoang Nhat Duy Le
- Joshua Davenport
- Sanskar Lamsal
1. **System Architecture**

   Overall Entity Relationship Diagram showing the relationship between entities![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.001.png)
























   UML Activity Diagrams:

- Login Activity

  ![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.002.png)















- Book new ticket activity![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.003.png)























- View ticket history activity![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.004.png)



















- Manage Ticket Activity

  ![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.005.png)
























1. **Backend Architecture**
1. **Building Blocks:**
- **Entities:** an entity represents a table in a relational database, and each entity instance corresponds to a row in that table.

  Ex: User Entity: table of all users (customers)

- **Repository:** we use this to create an abstraction layer between the data access and the business logic layer of an application. A repository is nothing but a class defined for an entity, with all the possible database operations.

  => By using it, we are promoting a more loosely coupled approach to access our data from the database.

  => Each entity needs a separate query to fetch/update directly and will require to have a repository to communicate with the database

- **Controllers:** the Controller in MVC architecture handles any incoming URL request.
- **DataContext:** The DataContext is the source of all entities mapped over a database connection. It tracks changes that you made to all retrieved entities and maintains an "identity cache" that guarantees that entities retrieved more than one time are represented by using the same object instance.

  Source: <https://learn.microsoft.com/en-us/dotnet/api/system.data.linq.datacontext?view=netframework-4.8.1>

- **Data Transfer Object (DTO):** an object that carries data, that can be transferred along with the request
- **Unit Of Work:** The Unit of Work pattern is used to group one or more operations (usually database CRUD operations) into a single transaction or “unit of work” so that all operations either pass or fail as one unit.

  Source: <https://dotnettutorials.net/lesson/unit-of-work-csharp-mvc/> 

1. **User Entity: require a UserRepository**

   Properties:

   - Id: every customer will have a unique ID

   - Username: username to login

   - Password: password to login

   - DateOfBirth

   - FullName: the real name of the customer

   - City

   - Country

   - Address

   - CreditCardNumber

   - PointsAvailable: available points to use when purchasing tickets

   - PointsUsed: the total amount of points that have been used by this customer

   - Credit: equivalent to the dollar amount, can be used to purchase tickets

   - Tickets: list of tickets that have been booked by this customer

   - UserRoles: role of this user

   - PhoneNumber

   - Email

   Relationship with other entities:

- Tickets: This is a one-to-many relationship. Each user can have multiple tickets but one ticket can be purchased by one user.
- UserRoles: this is a many-to-many relationship. Each user can have multiple roles and each role has multiple users.











  ![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.006.png)























1. **City Entity: do not require a repository**

   Properties:

   - Id: every city will have a unique ID

   - State: state of this city

   - Name: name of this city

   - Airport: service airport of this city

   - Latitude: latitude of the current city. Used to compute the distance between cities

   - Longitude: longitude of the current city. Used to compute the distance between cities

- Note: since it only needs one method, it is not necessary to create a repository for this entity.![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.007.png)










1. **Flight, Payment, and Ticket Entities: do not require a repository since we can fetch these entities along with their associated user.**

**Flight Properties**

\- Id: every flight has a unique Id

\- FlightNumber: every flight has a flight number

\- Origin: original city (airport)

\- Destination: destination city (airport)

\- LeaveTime: take off time

\- ArriveTime: arrive time

\- TravelDistance: total distance traveled

\- TravelDuration: total time (in hours) traveled

\- Model: the model of the plane used in this flight

\- Capacity: total number of passengers

\- Occupied: actual number of passengers

- Relationship with other entities:

  Ticket: this is a one-to-many relationship. Each ticket may have multiple flights (connection flights, round-trip tickets) but a flight can only be associated with one ticket.

**Payment Properties**

\- Id: every payment has a unique Id

\- Method: Cash or Credit

\- PayDate: the same as the day the ticket was booked

\- Amount: the number of dollars

\- CreditCardNumber: if paid by cash, what was the credit card number?

- Relationship with other entities:

  Ticket: this is a one-to-one relationship. Each ticket can only have one payment and a payment can only be associated with one ticket.

  **Ticket Properties**

  - Id: every payment has a unique Id

  - Flights: list of flights associated with this ticket

  - Payment: the payment associated with this ticket

  - Type: one-way or round trip

  - Amount: the price of this ticket

  - Points: the number of points that ticket is worth of

  - Status: check-in, canceled, or complete

- Relationship with other entities:

  AppUser: this is a one-to-many relationship. Each user can have multiple tickets but one ticket can be purchased by one user.




1. **Final Backend Architecture:![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.008.png)**




























1. **Frontend Architecture**

`		`\* We are using Angular to serve the front end of the application.

1. **Building Blocks:**
- **Components:** Components are the main building block for Angular applications. Each component consists of:
  - An HTML template that declares what renders on the page
  - A TypeScript class that defines the behavior
  - A CSS selector that defines how the component is used in a template
- **Services:** Components shouldn't fetch or save data directly. They should focus on presenting data and delegating data access to a service. They contain methods that maintain data throughout the life of an application, i.e., data is available all the time. 

  => The main objective of a service is to organize and share business logic, models, or data and functions with different components of an Angular application. They are usually implemented through dependency injection.

  => In this project, services are mainly used to fetch data from the database as well as update/delete.

1. **Final Backend Structure:**

![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.009.png)







































1. **Database Architecture**


   ![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.010.png)










1. **Map Structure & Flight Path**

We have decided to serve 10 airports. Each airport is the largest airport of that state (or one of the largest):

- Cleveland Hopkins International Airport	
- Dallas Fort Worth International Airport	
- Detroit Metro Wayne County Airport	
- Harry Reid International Airport	
- LaGuardia Airport	
- Miami International Airport	
- Nashville International Airport	
- Phoenix Sky Harbor International Airport	
- San Francisco International Airport	
- Seattle-Tacoma International Airport

![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.011.png)



















For this project, we will only hardcode paths from one airport to one airport. This will simulate the progress of generating a real path. We have come up with a table listed down below for more details:

- Straight: there is a straight path from one airport to another airport. No connection flight is needed.
- If it requires to have a connection flight, we have tried to choose to the shortest path leading to the destination.
- Each path can be used by both airports that it connects.

  => For example: we can go from Detroit to Harry Reid and we can go from Harry Reid to Detroit using the same path

![](Aspose.Words.1665e3cb-0081-46c1-be06-a9f270e0986d.012.png)


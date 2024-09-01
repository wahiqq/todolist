# Assignment Questions Answers

Question 1

What happens to the application on "cold start" (i.e. when you start it with no database, tables or data in the tables).

Answer: 
On a "cold start," when the application is started with no database, tables, or data in the tables, the following can happen:
1. Database Initialization: The application will attempt to connect to the SQLite database file specified (e.g., todolist.db).

2. If the database file does not exist or if the required tables are not present, the application will create the necessary tables. This is handled by the init_db function, which executes the SQL command to create the todolist table if it does not already exist.

3.Once the database and tables are set up, the application will be ready to handle incoming requests. At this point, the tables will be empty, and any operations that query the database will return empty results until data is added.



Question 2: What happens when multiple requests to the database happen concurrently.

Answer:
When multiple requests to the SQLite database happen concurrently in the provided code, the following can occur:
1. SQLite uses database-level locking to manage concurrent access. When a write operation is in progress, the database is locked to prevent other write operations from occurring simultaneously. Read operations can still proceed concurrently with other read operations but will be blocked by write operations.

2. SQLite supports a limited form of concurrency control which ensures that database operations are serialized, meaning they are executed one at a time. This prevents data corruption but can lead to contention and delays if many concurrent write operations are attempted.

3. If a request attempts to write to the database while it is locked, SQLite will return a "database is locked" error. The application should handle this error by retrying the operation after a short delay.

4. For applications with high concurrency requirements, SQLite may not be the best choice due to its locking mechanism. In such cases, a more robust database system with better concurrency support.


Question 3: What happens when any particular database or other operation fails in the middle.

Answer:
When a database or other operation fails in the middle, several things can happen depending on the nature of the failure:
1. If the failure occurs during a transaction, SQLite will automatically roll back the transaction to maintain database integrity. This means that any changes made during the transaction will be undone.

2. If the failure occurs and the database connection or cursor is not properly closed, it can lead to resource leaks. This can eventually exhaust the available connections or file handles, leading to further failures. 

3. The error will propagate up the call stack, potentially causing the application to return an error response to the client. If not handled properly, this can result in uninformative error messages or even application crashes.


Question 4: Can a user making a request corrupt your database or application in some way?

Answer:

Yes, a user making a request can potentially corrupt our database or application in several ways if proper safeguards are not in place.

1. SQL Injection; If user inputs are not properly sanitized, an attacker can execute arbitrary SQL commands, potentially corrupting or deleting data.(this was discussed in class also)
2. Concurrent Writes; If multiple write operations are not properly managed, it can lead to data corruption. 
3. Malformed Requests; If the application does not validate incoming requests properly, malformed data can be inserted into the database, leading to data integrity issues.
4. Resource Leaks; If database connections or cursors are not properly closed, it can lead to resource leaks, eventually exhausting available connections or file handles. 

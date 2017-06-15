# Dynamic fingerprinting
Author: Song Li, Olivia Orrell-Jones

Group: SECLAB in Lehigh University

## Description
This is a research project for dynamic fingerprinting, which means even some user change features of their computer, we can still fingerprint them

Specifically, our approach utilizes many novel OS and hardware level features, such as those from graphics cards, CPU, and installed writing scripts (Implementing). We extract these features by asking browsers to perform tasks that rely on corresponding OS and hardware functionalities. We are trying to figure out what really influence the fingerprints and define the distance between fingerprints
## Implementation
### Client
The whole client part is JS based in "client" dir. Some of the modules are generated from C or coffee.
Here is a list of usful description of dirs in "client":
- fingerprint: Including all files related to fingerprinting tests.
- js: Javascript part used for index.html

### Server

The server part is writen in python. Using apache2 and flask as the framework. 

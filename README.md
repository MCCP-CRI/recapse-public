RECAPSE Web Application
======

**Re**currence using **C**laims **a**nd **P**ROs for **S**EER **E**xpansion (RECAPSE) is an XGBoost model for 
predicting cancer second breast cancer events (recurrence and new breast primary) based on registry cancer incidence 
data linked with insurance enrollment and claims data.

The purpose of this tool is to provide prediction of second breast cancer events and improve the efficiency of 
registry operation effort to identify recurrences. Registries can utilize the results to manually check these cases 
for true recurrences. Users can adjust the cut-off value to control the sensitivity and specificity of the results 
based on their own specific data and resources available.

The utility is written in Python. A frontend in the form of a web application is also provided as 
either a standalone Flask application or a docker container. 

Running as a standalone application
===
If setting up as a python application, create a virtualenv:

    python -m venv env

Then activate it:

    source env/bin/activate

Then install the required dependencies using pip:

    pip install -r requirements.txt

To start the web application, execute `flask run`. This will start up a process listening on port 5000.

Running as a docker container
===
If you are receiving the docker image as a tarball file, first import it into docker with the 
`docker import` command, e.g. `docker import mccp-recapse.tar.gz mccp/recapse:latest`

To start the docker container, run `docker run -d mccp/recapse:latest`

The working directory is located at /app/instance and can be mounted for visibility into the intermediate files generated, e.g. 

    docker run -d -v /tmp/recapse-data:/app/instance mccp/recapse:latest

Port 5000 is the exposed port. This can be forwarded to the host:

    docker run -d -p 5000:5000 mccp/recapse:latest

Environment Options
===
Several options may be set when running the 

If a reverse proxy is being used, the application may need to be mounted in a sub-path (e.g. http://yourserver/recapse 
instead of http://yourserver/). If this is required, use the `APP_ROUTE_PREFIX` environment variable: 

    docker run -d -e APP_ROUTE_PREFIX=/recapse mccp/recapse:latest

By default, up to 2 workers are allowed. To change the number, use the `EXECUTOR_MAX_WORKERS` environment variable:

    docker run -d -e EXECUTOR_MAX_WORKERS=5 mccp/recapse:latest

By default, workers are started up as entirely separate processes. This has the benefit of being able to use multiple
CPU cores as each Python process can use a separate core. However, debugging information can be lost in this mode. 
To change to thread-based workers, use the `EXECUTOR_TYPE` environment variable:

    docker run -d -e EXECUTOR_TYPE=thread mccp/recapse:latest

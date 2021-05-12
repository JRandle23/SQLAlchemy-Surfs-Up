# Import dependencies 
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

import os
import sys

# Create file path 
print(os.path.dirname(__file__))

root_project_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, root_project_path)

hawaii_path = os.path.join(root_project_path, "hawaii.sqlite")

#####################################
# Database setup 
#####################################
engine = create_engine(f"sqlite:///{hawaii_path}")
conn = engine.connect()

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.measurement 

######################################
# Flask setup 
######################################
app = Flask(__name__)

#####################################
# Flask Routes 
#####################################
@app.route("/")
def Welcome():
    """List all available api routes"""
    return(
        f"Welcome to the Hawaii Climate Page API!<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"Precipitation data:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"Stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"Temperature observations from 8/18/2016-8/18/2017:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Minimum, Maximum and Average Temp for a given start date:<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"<br/>"
        f"Minimum, Maximum and Average Temp for a given start and end date:<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def Precipitation():
    session = Session(engine)
    # Query precipitation data 
    prcp_data = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary w/ date as the key and prcp as the value
    prcp_all = []
    for date,prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp 
        prcp_all.append(prcp_dict)
    return jsonify(prcp_all)

# Stations route
@app.route("/api/v1.0/stations")
def Stations():
    session = Session(engine)

    # Query list of stations
    station_data = session.query(Station.station).all()

    session.close()
    
    # Convrt list of tuples into a list
    stations = list(np.ravel(station_data))
    return jsonify(stations)

# Temperature route 
@app.route("/api/v1.0/tobs")
def Temperature():
    session = Session(engine)

    # most_recent_year_tobs is "2016-08-18" from query
    start_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    temp_data = session.query(Measurement.tobs). \
        filter(Measurement.station == "USC00519281"). \
        filter(Measurement.date >= start_date).all()
    
    session.close()

    # Convert list of tuples into a list
    temperatures = list(np.ravel(temp_data))
    return jsonify(temperatures=temperatures)

# Min, Max and Avg temp for a given start date or given start and end date
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def stats(start=None, end=None):
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]

    # Query start date only
    if not end:
        start_temps = session.query(*sel).\
            filter(Measurement.date >= start).all()
        print(start)
        temps = list(np.ravel(start_temps))
        return jsonify(temps)

    # Query both start and end dates
    start_end_date = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    # Convert list of tuples into normal list
    temps = list(np.ravel(start_end_date))
    return jsonify(temps)

 ######################################
if __name__ == '__main__':
    app.run(debug=True)







    


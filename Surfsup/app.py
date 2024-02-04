# Import the dependencies.
import numpy as np

from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt


#################################################
# Database Setup
#################################################
# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Homepage
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/><br/>"
        f"IMPORTANT: use the format yyy-mm-dd for dates.<br/>"
    )


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                         filter(Measurement.date >= query_date).all()

    session.close()


    # Convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    
    # Query list of stations
    station_list = session.query(Station.station).all()

    session.close()

    # Convert the query results to a list
    stations = [station[0] for station in station_list]

    return jsonify(stations)

# Temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    
    # Get the most active station ID
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year from the last date in the data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query temperature observations for the most active station in the last 12 months
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= query_date).all()

    session.close()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Temperature statistics route
@app.route("/api/v1.0/<start_date>")
def temp_stats_start(start_date):
    # Calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    session = Session(engine) 

    temp_stats = session.query(func.min(Measurement.tobs),
                               func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).\
                               filter(Measurement.date >= start_date).all()

    session.close()

    # Convert the query results to a list of dictionaries
    temp_stats_list = [{"Min Temperature": temp_stats[0][0],
                        "Avg Temperature": temp_stats[0][1],
                        "Max Temperature": temp_stats[0][2]}]

    return jsonify(temp_stats_list)

# Temperature statistics route for a specified start date and end date
@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_stats_range(start_date, end_date):

    session = Session(engine)
    
    # Calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive
    temp_stats = session.query(func.min(Measurement.tobs),
                               func.avg(Measurement.tobs),
                               func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    session.close()

    # Convert the query results to a list of dictionaries
    temp_stats_list = [{"Min Temperature": temp_stats[0][0],
                        "Avg Temperature": temp_stats[0][1],
                        "Max Temperature": temp_stats[0][2]}]

    return jsonify(temp_stats_list)

if __name__ == "__main__":
    app.run(debug=True)


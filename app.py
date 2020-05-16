import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the home page!<br/>"
        f"Please enter dates in yyyy-mm-dd format.<br/>"
        f"Available Routes:<br/>"
        f"<a href= '/api/v1.0/precipitation'>Precipitation<br/>"
        f"<a href= '/api/v1.0/stations'>Station List<br/>"
        f"<a href= '/api/v1.0/tobs'>Temperature Observations<br/>"
        f"<a href= '/api/v1.0/<start>'>Start Date<br/>"
        f"<a href= '/api/v1.0/<start>/<end>'>Start and End Date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    twelve_mo_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    last_12_precip = session.query(Measurement.date, func.sum(Measurement.prcp)).\
        filter(Measurement.date >= twelve_mo_ago).\
        group_by(Measurement.date).all()
    
    session.close()
    
    precipitation = dict(last_12_precip)
    
    return jsonify(last_12_precip)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Measurement.station, Station.name, Station.latitude, Station.longitude, Station.elevation).\
            filter(Measurement.station == Station.station).distinct().all()
    
    session.close()
    
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)
    last = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    twelve_mo_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    temp_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= twelve_mo_ago).all()
    
    session.close()
    
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def temp_range_to_end(start):
    session = Session(engine)

    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    
    temp_summary = session.query(*sel).\
        filter(Measurement.date >= start).all()
    
    session.close()
    
    return jsonify(temp_summary)
    
    return jsonify({"error": "Date not found."}), 404


@app.route("/api/v1.0/<start>/<end>")
def temp_date_range(start, end):
    session = Session(engine)
        
    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    
    temp_summary = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()
    
    return jsonify(temp_summary)
    
    
    return jsonify({"error": "Date not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
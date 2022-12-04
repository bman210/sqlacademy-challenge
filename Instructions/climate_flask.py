# imports
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import dt

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station


# Create an app using Flask
app = Flask(__name__)

@app.route("/")
def home():
    """Welcome to my climate analysis page. Below is a list of all available api routes!"""
    return(
        f'/api/v1.0/precipitation (this contains relevant information about the precipitation patterns in Hawaii between 2016-08-23 and 2017-08-23)'
        f'/api/v1.0/stations (this contains a list of all weather stations used to collect data)'
        f'/api/v1.0/tobs (this contains temperature information throughout Hawaii for the most activate weather station (USC00519281) between 2016-08-23 and 2017-08-23'
        f'/api/v1.0/<start> (returns a list of minimum, average and maximum temperature found at weather station (USC00519281) from a given starting position to 2017-08-23.
        the start date must be later than or equal to 2016-08-23')
        f'/api/v1.0/<start>/<end> (returns a list of minimum, average and maximum temperature found at weather station (USC00519281).
        Starting and ending dates are provided by the user and all dates must fall between 2016-08-23 and 2012-08-23'

########################################################################################


@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create a session link from python to DB
    session = Session(engine)

    selection = [measurement.date, measurement.prcp]
    sub_one_year = dt.date(2017,8,23) - dt.timedelta(days= 365)
    precip_data = session.query(*selection).\
        filter(measurement.date >= sub_one_year).\
        order_by(measurement.date).all()
    
    session.close()

    precip_list = []
    for date, prcp in precip_data:
        precip_dict = {}
        precip_dict['Date'] = date
        precip_dict['Precipitation'] = prcp
        precip_list.append(precip_dict)
    
    return jsonify(precip_list)

#####################################################################################


@app.route('/api/v1.0/stations')
def stations_list():
    session = Session(engine)

    station_count = session.query(station.station).all()

    session.close()

    return jsonify (station_count)


###################################################################################


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    temp_obs_pastyear = session.query(measurement.date,measurement.tobs).\
        filter (measurement.station == 'USC00519281').filter(measurement.date >= sub_one_year).\
        order_by(measurement.date).all()
    
    session.close()

    temp_list = []
    for date,tobs in temp_obs_pastyear:
        tobs_dict = {}
        tobs_dict['Date'] = date
        tobs_dict['tobs'] = tobs
        temp_list.append(tobs_dict)
    
    return jsonify(temp_list)

###################################################################################


@app.route('/api/v1.0/<start>')
def start():
    session = Session(engine)
    
    #choosen start date and end date locked at '2017-08-23'
    end_date = dt.date(2017,8,23)
    start_date = dt.date(input(f'put year as YYYY'),input(f'put month as M or MM'),input(f'put day as D or DD'))

    temps = [measurement.station,
        func.max(measurement.tobs),
        func.min(measurement.tobs),
        func.avg(measurement.tobs)]

    temp_station = session.query(*temps).\
        filter (measurement.station == 'USC00519281').filter (measurement.date >= start_date).filter(measurement.date =< end_date).all()








    session.close()


###################################################################################

@app.route('/api/v1.0/<start>/<end>')
def start_end():






if __name__ == "__main__":
    app.run(debug=True)
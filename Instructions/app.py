# imports
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
    
    return(
        f"""Welcome to my climate analysis page. Below is a list of all available api routes!<br/>"""
        f'<br/>'
        f'/api/v1.0/precipitation (This contains relevant information about the precipitation patterns in Hawaii between 2016-8-23 and 2017-8-23)<br/>'
        f'/api/v1.0/stations (This contains a list of all weather stations used to collect data)<br/>'
        f'/api/v1.0/tobs (This contains temperature information throughout Hawaii for the most activate weather station (USC00519281) between 2016-8-23 and 2017-8-23<br/>'
        f'/api/v1.0/date (Returns a list of minimum, average and maximum temperature found at weather station (USC00519281) from a given starting posdateition to 2017-8-23.<br/>'
        f'--For this api please input a start date in the form of YYYY-M(M)-D(D).The start date must be later than or equal to 2016-8-23)<br/>'
        f'/api/v1.0/date_end (Returns a list of minimum, average and maximum temperature found at weather station (USC00519281).<br/>' 
        f'--Starting and ending dates are provided by the user and all dates must fall between 2016-8-23 and 2017-8-23. Input a start date and end date in the form of YYYY-M(M)-D(D).<br/>'
        f'--An example of of this api is = http://localhost:5000/api/v1.0/date_end/2016-8-30/2017-6-11')

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
        precip_dict = {date:prcp}
        # precip_dict['Date'] = date
        # precip_dict['Precipitation'] = prcp
        precip_list.append(precip_dict)
    
    return jsonify(precip_list)

#####################################################################################


@app.route('/api/v1.0/stations')
def stations_list():
    session = Session(engine)

    station_count = session.query(station.station).all()

    session.close()

    all_names = list(np.ravel(station_count))
    # stat_count_list = []
    # for s in station_count:
    #     stat_count_dict = {}
    #     stat_count_dict['Station'] = s
    #     stat_count_list.append(stat_count_dict)

    return jsonify(all_names)


###################################################################################


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    sub_one_year = dt.date(2017,8,23) - dt.timedelta(days= 365)

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


@app.route('/api/v1.0/date/<start_date>')
def start(start_date):
    session = Session(engine)
    
    #choosen start date and end date locked at '2017-08-23'
    end_date = dt.date(2017,8,23)
    actual_start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()

    temps = [measurement.station,
        func.max(measurement.tobs).label('max_value'),
        func.min(measurement.tobs).label('min_value'),
        func.avg(measurement.tobs).label('average')]

    temp_station = session.query(*temps).\
        filter(measurement.station == 'USC00519281').filter(measurement.date.between(actual_start_date,end_date)).all()
    # start_temp_list = [
    #     {'Station': temps[0]},
    #     {'Maximum Temperature': temps[1]},
    #     {'Minimum Temperature': temps[2]},
    #     {'Average Temperature': temps[3]}]

    session.close()

    start_temp_list = []
    for station in temp_station:
        start_temp_dict = {}
        start_temp_dict['Station'] = station.station
        start_temp_dict['Max_value'] = station.max_value
        start_temp_dict['Min_value'] = station.min_value
        start_temp_dict['Average'] = station.average
        start_temp_list.append(start_temp_dict)
    

    return jsonify(start_temp_list)

    


###################################################################################

@app.route('/api/v1.0/date_end/<start_date>/<end_date>')
def start_end(start_date,end_date):
    session = Session(engine)

    actual_end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    actual_start_date =  dt.datetime.strptime(start_date, "%Y-%m-%d").date()

    temps = [measurement.station,
        func.max(measurement.tobs).label('max_value'),
        func.min(measurement.tobs).label('min_value'),
        func.avg(measurement.tobs).label('average')]

    temp_station = session.query(*temps).\
        filter(measurement.station == 'USC00519281').filter(measurement.date.between(actual_start_date,actual_end_date)).all()

    start_temp_list = []
    for station in temp_station:
        start_temp_dict = {}
        start_temp_dict['Station'] = station.station
        start_temp_dict['Max_value'] = station.max_value
        start_temp_dict['Min_value'] = station.min_value
        start_temp_dict['Average'] = station.average
        start_temp_list.append(start_temp_dict)

    return jsonify(start_temp_list)



if __name__ == "__main__":
    app.run(debug=True)
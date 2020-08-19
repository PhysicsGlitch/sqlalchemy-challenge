import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, funcfilter

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Saved references to the table
measurement = Base.classes.measurement
stations = Base.classes.station

# Flask Setup
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
 """List all available api routes."""
 return (
  f"Available Routes:<br/>"
  f"/api/v1.0/precipitation_values<br/>"
  f"/api/v1.0/station_names<br/>"
  f"/api/v1.0/tobs<br/>"
  f"/api/v1.0/<start><br/>"
  f"/api/v1.0/<start>/<end>"
 )


# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

@app.route("/api/v1.0/precipitation_values")
def precipitation_values():
 # Create our session (link) from Python to the DB
 session = Session(engine)

 """Return a list of precipitation measurments"""
 # Query prcp measurements
 results = session.query(measurement.date, measurement.prcp).all()

 session.close()

 # Create a dictionary from the row data and append to a list of all_prcp
 all_precipitation = []
 for date, precipitation in results:
  precipitation_dict = {date: precipitation}
  all_precipitation.append(precipitation_dict)

 return jsonify(all_precipitation)


# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/station_names")
def station_names():
 session = Session(engine)

 results = session.query(stations.station, stations.name).all()

 session.close()

 station_list = []
 for numb, name in results:
  station_dict = {}
  station_dict["number"] = numb
  station_dict["name"] = name
  station_list.append(station_dict)

 return jsonify(station_list)



# Query the dates and temperature observations of the most active station for the last year of data.

@app.route("/api/v1.0/tobs")
def tobs():
 session = Session(engine)

 active_station_query = 'SELECT station, date, tobs FROM measurement ' \
                        'WHERE station = "USC00519281" AND measurement.date > "2016-08-23"'
 most_active = engine.execute(active_station_query).fetchall()

 session.close()

 top_station = []
 for station_name, date, tobs in most_active:
  top_dict = {}
  top_dict['station'] = station_name
  top_dict['date'] = date
  top_dict['tobs'] = tobs
  top_station.append(top_dict)

 return jsonify(top_station)

#  Values for start date range

@app.route("/api/v1.0/<start_date>")
def start(start_date):
  session = Session(engine)

  sel = [measurement.date, func.max(measurement.tobs), func.min(measurement.tobs), func.avg(measurement.tobs)]
  results = session.query(*sel).\
       filter(measurement.date >= start_date).all()

  session.close()

  yearly_values = []
  for date, max_val, min_val, avg_val, in results:
   yearly_value_dict = {}
   yearly_value_dict["high_temp"] = max_val
   yearly_value_dict["low_temp"] = min_val
   yearly_value_dict["avg_temp"] = avg_val
   yearly_values.append(yearly_value_dict)

  return jsonify(yearly_values)

@app.route("/api/v1.0/<start_date>/<end_date>")
def date_range(start_date, end_date):
  session = Session(engine)

  sel = [measurement.date, func.max(measurement.tobs), func.min(measurement.tobs), func.avg(measurement.tobs)]
  results = session.query(*sel).\
       filter(measurement.date >= start_date).\
       filter(measurement.date <= end_date).all()

  session.close()

  yearly_values = []
  for date, max_val, min_val, avg_val, in results:
   yearly_value_dict = {}
   yearly_value_dict["high_temp"] = max_val
   yearly_value_dict["low_temp"] = min_val
   yearly_value_dict["avg_temp"] = avg_val
   yearly_values.append(yearly_value_dict)

  return jsonify(yearly_values)


if __name__ == '__main__':
 app.run(debug=True)

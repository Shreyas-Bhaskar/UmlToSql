from flask import Flask, render_template, request
from plantuml_parser import parse_plantuml_to_sql

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        plantuml_code = request.form['plantuml_code']
        sql_outputx = parse_plantuml_to_sql(plantuml_code)
        sql_output = '''
        -- Table for Staff
CREATE TABLE Staff (
  staff_id INT PRIMARY KEY,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  job_title VARCHAR(255)
);

-- Table for Station
CREATE TABLE Station (
  station_name VARCHAR(255) PRIMARY KEY,
  location_longitude FLOAT,
  location_latitude FLOAT,
  zone VARCHAR(255)
);

-- Table for Route
CREATE TABLE Route (
  route_name VARCHAR(255) PRIMARY KEY,
  fare FLOAT,
  days_of_week VARCHAR(255),
  mode VARCHAR(255),
  number_of_stops INT
);

-- Table for Vehicle
CREATE TABLE Vehicle (
  vehicle_number VARCHAR(255) PRIMARY KEY,
  passenger_capacity INT,
  current_location_longitude FLOAT,
  current_location_latitude FLOAT,
  last_maintenance_date DATE
);

-- Table for Trip
CREATE TABLE Trip (
  route_name VARCHAR(255),
  scheduled_departure_time DATETIME,
  scheduled_arrival_time DATETIME,
  actual_departure_time DATETIME,
  actual_arrival_time DATETIME,
  vehicle_status VARCHAR(255),
  PRIMARY KEY (route_name, scheduled_departure_time),
  FOREIGN KEY (route_name) REFERENCES Route(route_name)
);

-- Table for CharlieCard
CREATE TABLE CharlieCard (
  card_number VARCHAR(255) PRIMARY KEY,
  current_balance FLOAT,
  user_email VARCHAR(255)
);

-- Table for StationManager
CREATE TABLE StationManager (
  staff_id INT PRIMARY KEY,
  FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);

-- Table for VehicleOperator
CREATE TABLE VehicleOperator (
  staff_id INT PRIMARY KEY,
  FOREIGN KEY (staff_id) REFERENCES Staff(staff_id)
);

-- Table for StationRoute (Associative Entity)
CREATE TABLE StationRoute (
  station_name VARCHAR(255),
  route_name VARCHAR(255),
  sequence_number INT,
  PRIMARY KEY (station_name, route_name),
  FOREIGN KEY (station_name) REFERENCES Station(station_name),
  FOREIGN KEY (route_name) REFERENCES Route(route_name)
);
'''
        return render_template('index.html', sql_output=sql_output)
    return render_template('index.html', sql_output=None)

if __name__ == '__main__':
    app.run(debug=True)

import argparse
import json
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from beam_nuggets.io import relational_db

def filter_missing_measurement(element):
    return element.get('pressure') is not None and element.get('temperature') is not None

def convert_units(element):
    # kPa to psi
    element['pressure'] = element['pressure'] / 6.895
    # Celsius to Fahrenheit
    element['temperature'] = element['temperature'] * 1.8 + 32
    return element

def run(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', dest='input', required=True,
                        help='Input topic to read smart meter measurements.')
    parser.add_argument('--output', dest='output', required=True,
                        help='Output topic to write processed measurements.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    # Database configuration for MySQL 
    connection_config = relational_db.SourceConfiguration(
        drivername='mysql+pymysql',
        host='', # ADD UR OWN DB IP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        port=3306,
        username='usr',
        password='sofe4630u',
        database='Readings'
    )

    # Table Configuration for Preprocessed records
    table_config = relational_db.TableConfiguration(
        name='preprocessed_records',
        create_if_missing=True,
        primary_key_columns=['time']
    )


    with beam.Pipeline(options=pipeline_options) as p:
        readings = (p | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(topic=known_args.input)
                     | "Convert from JSON to Python Object" >> beam.Map(lambda x: json.loads(x)))

        # Write to database
        readings | "Write to Database" >> relational_db.Write(source_config=connection_config, table_config=table_config)


        filtered_readings = readings | "Filter Missing Measurements" >> beam.Filter(filter_missing_measurement)
        processed_readings = filtered_readings | "Convert Units" >> beam.Map(convert_units)

        (processed_readings | "Convert from Python Object to JSON and encode as UTF-8" >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
                            | "Write to Pub/Sub" >> beam.io.WriteToPubSub(topic=known_args.output))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
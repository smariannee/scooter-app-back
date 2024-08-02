import json
import pymysql

# Configuración de la conexión a la base de datos
rds_host = "database-cafe-balu.cziym6ii4nn7.us-east-2.rds.amazonaws.com"
rds_user = "baluroot"
rds_password = "baluroot"
rds_db = "scooters"

def lambda_handler(event, __):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token"
    }

    try:
        if 'pathParameters' not in event or 'id' not in event['pathParameters']:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "MISSING_ID"
                }),
            }

        id = event['pathParameters']['id']

        if not valid_id(id):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "INVALID_ID"
                }),
            }

        if not exists(id):
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({
                    "message": "SCOOTER_NOT_FOUND"
                }),
            }

        if delete_scooter(id):
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "SCOOTER_DELETED"
                }),
            }
        else:
            raise Exception("ERROR DELETING SCOOTER")

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "message": "INTERNAL_SERVER_ERROR",
                "error": str(e)
            }),
        }

def connect_to_database():
    try:
        connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_password, db=rds_db)
        return connection
    except pymysql.MySQLError as e:
        raise Exception("ERROR CONNECTING TO DATABASE: " + str(e))

def valid_id(id):
    return id.isdigit() and int(id) > 0

def exists(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("select * from scooters where id = %s", (id,))
    result = cursor.fetchone()
    connection.close()
    return result is not None

def delete_scooter(id):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("delete from scooters where id = %s", (id,))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
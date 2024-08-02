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
        "Access-Control-Allow-Methods": "PUT, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token"
    }

    try:
        body = json.loads(event.get('body', '{}'))

        if not 'brand' in body or not 'model' in body or not 'autonomy' in body or not 'weight' in body or not 'id' in body:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "MISSING_FIELDS",
                }),
            }

        id = body.get('id')
        brand = body.get('brand')
        model = body.get('model')
        autonomy = body.get('autonomy')
        weight = body.get('weight')

        if not brand or not model or not autonomy or not weight or not id:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "MISSING_FIELDS",
                }),
            }

        if int(id) <= 0:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "INVALID_ID",
                }),
            }

        if not exists(id):
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({
                    "message": "SCOOTER_NOT_FOUND",
                }),
            }

        if duplicate(id, model):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "DUPLICATE_SCOOTER",
                }),
            }

        if update_scooter(id, brand, model, autonomy, weight):
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "SCOOTER_UPDATED",
                }),
            }
        else:
            raise Exception("ERROR UPDATING SCOOTER")

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

def exists(id):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("select * from scooters where id = %s", (id,))
    result = cursor.fetchone()
    connection.close()
    return result is not None

def duplicate(id, model):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("select * from scooters where id != %s and model = %s", (id, model))
    result = cursor.fetchone()
    connection.close()
    return result is not None

def update_scooter(id, brand, model, autonomy, weight):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("update scooters set brand = %s, model = %s, autonomy = %s, weight = %s where id = %s", (brand, model, autonomy, weight, id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        return False
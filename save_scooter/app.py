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
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token"
    }

    try:
        body = json.loads(event.get('body', '{}'))

        if not 'brand' in body or not 'model' in body or not 'autonomy' in body or not 'weight' in body:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "MISSING_FIELDS",
                }),
            }

        brand = body.get('brand')
        model = body.get('model')
        autonomy = body.get('autonomy')
        weight = body.get('weight')

        if not brand or not model or not autonomy or not weight:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "MISSING_FIELDS",
                }),
            }

        if duplicate(model):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "DUPLICATE_SCOOTER",
                }),
            }

        return save_scooter(brand, model, autonomy, weight, headers)

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "message": "INTERNAL_SERVER_ERROR",
                "error": str(e)
            })
        }

def connect_to_database():
    try:
        connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_password, db=rds_db)
        return connection
    except pymysql.MySQLError as e:
        raise Exception("ERROR CONNECTING TO DATABASE: " + str(e))

def duplicate(model):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("select * from scooters where model = %s;", model)
    result = cursor.fetchall()
    return len(result) > 0

def save_scooter(brand, model, autonomy, weight, headers):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("insert into scooters(brand, model, autonomy, weight) values(%s, %s, %s, %s)", (brand, model, autonomy, weight))
        connection.commit()

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "message": "SCOOTER_SAVED",
            }),
        }
    except Exception as e:
        raise Exception("ERROR SAVING SCOOTER")
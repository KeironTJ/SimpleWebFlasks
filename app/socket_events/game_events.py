from app.socket_events import bp
from app import sock
from app.game.buildings.building_services import GameBuildingService
import json
import time
import logging

logging.basicConfig(level=logging.DEBUG)


@sock.route('/echo')
def echo(ws):
    while True:
        data = ws.receive()
        if data is None:
            break
        ws.send(data)


@sock.route('/ws')
def websocket(ws):
        while True:
            message = ws.receive()
            if message:
                logging.debug(f"Received message: {message}")
                data = json.loads(message)
                chat_message = data.get('message')
                logging.debug(f"Chat message: {chat_message}")
                response = {
                    'type': 'chat_message',
                    'message': chat_message
                }
                ws.send(json.dumps(response))
                logging.debug(f"Sent response: {response}")
            # Add more event handling as needed


@sock.route('/ws/building_resource')
def building_resource_ws(ws):
    while True:
        message = ws.receive()
        if message:
            logging.debug(f"Received message: {message}")
            data = json.loads(message)
            if data['event'] == 'resource_update':
                building_progress_id = data.get('building_progress_id')
                logging.debug(f"Building progress ID: {building_progress_id}")
                if building_progress_id:
                    try:
                        buildingservice = GameBuildingService(building_progress_id=building_progress_id)
                        while True:
                            buildingservice.calculate_accrued_resources()  # Assuming this method exists
                            response = {
                                'event': 'resource_update',
                                'accrued_cash': buildingservice.building.accrued_cash,
                                'accrued_wood': buildingservice.building.accrued_wood,
                                'accrued_stone': buildingservice.building.accrued_stone,
                                'accrued_metal': buildingservice.building.accrued_metal
                            }
                            ws.send(json.dumps(response))
                            logging.debug("Building service processed successfully")
                            time.sleep(60)  # Send updates every 5 seconds
                    except ValueError as e:
                        error_message = {'error': str(e)}
                        ws.send(json.dumps(error_message))
                        logging.error(f"Error: {error_message}")
                        break
                else:
                    error_message = {'error': 'building_progress_id is missing'}
                    ws.send(json.dumps(error_message))
                    logging.error(f"Error: {error_message}")
                    break
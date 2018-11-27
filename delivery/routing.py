from channels import route
from store import consumers

ASGI_APPLICATION = "delivery.asgi.application"

channel_routing = [
	# websocket channels to store consumers

	route("websocket.connect", consumers.ws_connect),
	route("websocket.receive", consumers.ws_receive),
]
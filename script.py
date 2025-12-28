import requests
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

COLAB_URL = "https://e0abc01814b3.ngrok-free.app/compute"

async def offer(request):
    data = await request.json()

    pc = RTCPeerConnection()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(msg):
            print("Render received:", msg)

            r = requests.post(
                COLAB_URL,
                json={"message": msg},
                timeout=10
            ).json()

            channel.send(r["reply"])

    offer = RTCSessionDescription(
        sdp=data["sdp"],
        type=data["type"]
    )

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

app = web.Application()
app.router.add_post("/offer", offer)

web.run_app(app, port=10000)

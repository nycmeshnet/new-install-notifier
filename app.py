from flask import Flask, request, jsonify
import json
import sys
import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

with open("channels.json") as f:
	channels = json.load(f)

slack = App(token=os.environ.get("SLACK_BOT_TOKEN"))

app = Flask(__name__)

def post_install(channel_id, install, name, unit, phone, email, location, ticket, description):
    try:
        response = slack.client.chat_postMessage(
            channel=channel_id,
            blocks=[
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Install* <https://map.nycmesh.net/nodes/{install}|{install}> - {name}\n*Location:* {location}\n*Unit:* {unit}\n*Phone Number:* {phone}\n*E-Mail Address:* {email}\n*Ticket:* <https://support.nycmesh.net/scp/tickets.php?number={ticket}|#{ticket}>\n*Description:* {description}"}
                }
            ],
            text=f"*Install* {install} - {name} | *Location:* {location} | *Unit:* {unit} | *Phone Number:* {phone} | *E-Mail Address:* {email} | * Description:* {description}"
        )
        print(f"Message sent: {response['ts']}")
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)  # Parse JSON
        # Pretty-print JSON to stdout
        print(json.dumps(data, indent=4), file=sys.stdout, flush=True)

        id = data["data"]["id"]
        install = data["data"]["install_number"]
        node = data["data"]["node"]["network_number"]
        unit = data["data"]["unit"]
        member_id = data["data"]["member"]["id"]
        building_id = data["data"]["building"]["id"]

        headers = {
            "accept": "application/json",
            "Authorization": "Token " + os.environ.get("MESHDB_API_KEY"),
        }

        members_url = f"https://db.nycmesh.net/api/v1/members/{member_id}/"
        response = requests.get(members_url, headers=headers)

        if response.status_code == 200:
            member = response.json()
            name = member.get("name")
            email = member.get("primary_email_address")
            phone = member.get("phone_number")

            try:
                channel_id = channels[str(node)]["channel_id"]
                description = channels[str(node)]["description"]
            except KeyError as e:
                print("204, Error message:", e)
                return jsonify({"status": "success"}), 204
        else:
            print("MeshDB Error (getting member):", response.status_code, response.text)
            return jsonify({"status": "error", "message": str(response.text)}), response.status_code

        buildings_url = f"https://db.nycmesh.net/api/v1/buildings/{building_id}/"
        buildings_response = requests.get(buildings_url, headers=headers)

        if buildings_response.status_code == 200:
            new_building = buildings_response.json()
            street_address = new_building.get("street_address")
            city = new_building.get("city")
            state = new_building.get("state")
            zip_code = new_building.get("zip_code")
            location = street_address + ", " + city + ", " + state + ", " + zip_code
        else:
            print("MeshDB Error (getting buildings):", buildings_response.status_code, buildings_response.text)
            return jsonify({"status": "error", "message": str(buildings_response.text)}), buildings_response.status_code

        installs_url = f"https://db.nycmesh.net/api/v1/installs/{id}/"
        installs_response = requests.get(installs_url, headers=headers)

        if installs_response.status_code == 200:
            new_install = installs_response.json()

            # Retry up to 3 additional times if ticket_number is None
            ticket_number = new_install.get("ticket_number")
            retries = 0
            while ticket_number is None and retries < 3:
                print(f"No ticket yet, retrying ({retries + 1}/3)...")
                time.sleep(3)
                installs_response = requests.get(installs_url, headers=headers)
                if installs_response.status_code != 200:
                    print("MeshDB Error (retrying install):", installs_response.status_code, installs_response.text)
                    return jsonify({"status": "error", "message": str(installs_response.text)}), installs_response.status_code
                new_install = installs_response.json()
                ticket_number = new_install.get("ticket_number")
                retries += 1
            if ticket_number is None:
                print("No ticket after retries!")
                return jsonify({"status": "no ticket"}), 500

        else:
            print("MeshDB Error (getting install):", installs_response.status_code, installs_response.text)
            return jsonify({"status": "error", "message": str(installs_response.text)}), installs_response.status_code

        post_install(channel_id=channel_id, install=install, name=name, unit=unit, phone=phone, email=email, location=location, ticket=ticket_number, description=description)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"400, Error: {e}", file=sys.stderr, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

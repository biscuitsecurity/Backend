from flask import Blueprint, request

import json
from backend.storage import ethereum as eth
from backend.storage import ipfs
import asyncio

bp = Blueprint("contract", __name__, url_prefix='/contract')


#####################
# contract routes
#####################
@bp.route('/incidents', methods=['GET'])
async def get_incidents():
    incidents = eth.get_incidents()
    incidents_full = await asyncio.gather(*[eth.get_incident(i) for i in incidents])
    comments_full = await asyncio.gather(*[
        asyncio.gather(*[
            eth.get_comment(i['content'], j) for j, c in enumerate(i['commentList'])
        ])
        for i in incidents_full])

    for j, i in enumerate(comments_full):
        incidents_full[j]['comments'] = i
    return json.dumps(incidents_full)


# return all incident data
@bp.route('/incidents', methods=['POST'])
async def add_incident():
    attachment = request.files['attachment']
    attachment_name = request.form.get('attachmentName')
    incident = json.loads(request.form.get('incident'))
    ipfsRefs = await asyncio.gather(*[
        ipfs.write_json(incident),
        ipfs.write_file(attachment)
    ])
    eth.add_incident(ipfsRefs[0], [(attachment_name, eth.ipfs2bytes(ipfsRefs[1]))])
    return '', 200


@bp.route('/incidents/comments', methods=['POST'])
async def add_incident_comment():
    body = request.get_json()
    comment = body['content']
    incident = body['incident']
    ipfsRef = await ipfs.write_json(comment)
    eth.add_comment(incident, eth.ipfs2bytes(ipfsRef))
    return '', 200

from flask import Blueprint
from backend.storage import ipfs

bp = Blueprint("ipfs", __name__, url_prefix='/ipfs')


@bp.route('/<string:ref>', methods=['GET'])
def read_ipfs(ref):
    return ipfs.read(ref)


@bp.route('', methods=['POST'])
def write_ipfs():
    pass

import os
from pathlib import Path

import firebase_admin

firebase_dir = f"{Path(__file__).parent.parent}/firebase"
cred = firebase_admin.credentials.Certificate(os.path.join(firebase_dir, 'key.json'))

firebase_client = firebase_admin.initialize_app(credential=cred)

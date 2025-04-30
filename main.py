# This file is part of magic-8-bot and is licensed under the MIT License.
# See the LICENSE file in the root directory for full license text.

import uvicorn
from bot.webhook import app
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

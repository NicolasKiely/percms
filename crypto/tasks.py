from percms.celery import app
import scripting.utils
from crypto import batch


@app.task()
def poloniex_candles_update(api_key_name=None):
    logger = scripting.utils.Logging_Runtime('Batch_Server')
    batch.POST_poloniex_candles_update(logger, api_key_name)

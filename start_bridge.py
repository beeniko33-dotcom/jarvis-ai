import sys
import logging

logging.basicConfig(filename='bridge.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info('Starting bridge using %s', sys.executable)
    try:
        import uvicorn
        from api.bridge import app
        logger.info('uvicorn imported, starting server')
        # Run the ASGI server; this will block
        uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')
    except Exception as e:
        logger.exception('Failed to start bridge: %s', e)
        print('ERROR starting bridge; see bridge.log for details')

if __name__ == '__main__':
    main()

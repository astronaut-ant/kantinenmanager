from . import app

@app.route('/health')
def health():
    response_dict = {
        "health_status":"OK"
    } 
    return response_dict
from flask import Flask, render_template, request, make_response, jsonify
import redis
from tasks import count_words
from rq import Queue
import string
import functools
import secrets
from stdlink import location, phone, url, mail, download

N = 16

r = redis.Redis(host='redis')
q = Queue(connection=r)
app = Flask(__name__)

@functools.lru_cache() 
def init_email():
    download.download_user_data()
    return mail.EmailParser(user=True)


def input_error():
    return jsonify({
        "error": {
            "code": 404,
            "message": "Input params not properly given"}
    })


def success_return(data):
    return jsonify({
        "data": data,
    })


def error_return(e):
    return jsonify({
        "error": {
            "code": 404,
            "message": f"Error {e} has occured", }
    })


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/api/phone/')
def api_phone():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    country_code = request.args.get("country_code")
    try:
        final_data = phone.extract_phonenumber(input_, country_code)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/phone/telephone/')
def api_phone_telephone():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        final_data = phone.extract_phonenumber_from_telephone(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/phone/whatsapp/')
def api_phone_whatsapp():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        final_data = phone.extract_phonenumber_from_whatsapp(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/phone/viber/')
def api_phone_viber():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        final_data = phone.extract_phonenumber_from_viber(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/country/')
def api_country():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        final_data = location.extract_country(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/country_code/')
def api_country_code():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        final_data = location.extract_country_code(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/country_zip/')
def api_country_zip():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        final_data = location.extract_us_zip(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/url/extract/')
def api_url_extract():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        final_data = url.extract_urls_from_text(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/url/clean/appstore/')
def api_url_clean_appstore():
    input_ = request.args.get("input")
    host = request.args.get("host")
    if not input_ or not host:
        return input_error()
    try:
        final_data = url.extract_urls_from_text(input_, host)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/url/get_host_meta/')
def api_url_get_host_meta():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    email = request.args.get("email")
    try:
        final_data = url.get_host_meta(input_, email)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/url/clean/')
def api_url_clean():
    input_ = request.args.getlist("input")
    if not input_:
        return input_error()
    try:
        final_data = url.clean_http_urls(input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/api/email/')
def api_email():
    input_ = request.args.get("input")
    if not input_:
        return input_error()
    try:
        email = init_email()
        final_data = email.extract_emails(text=input_)
        return success_return(final_data)
    except Exception as e:
        return error_return(e)


@app.route('/sulav')
def sulav_me():
    return render_template('sulav.html')


@app.route('/add_task', methods=('GET', 'POST'))
def add_task():
    jobs = q.jobs
    message = None
    if request.method == "POST":
        url = request.form['url']
        if url:
            task = q.enqueue(count_words, url)
            job_ids = task.id
            cookie_key = request.cookies.get('cookieid')
            if cookie_key == None:
                cookie_key = str(''.join(secrets.choice(string.ascii_uppercase + string.digits)
                                         for i in range(N)))
            jobs = q.jobs
            q_length = len(q)
            r.hset(cookie_key, url, job_ids)
            message = f"The result is {task} and the jobs queued are {q_length}"
            resp = make_response(render_template(
                "add_task.html", message=message, jobs=jobs))
            resp.set_cookie("cookieid", cookie_key)
            return resp
    return render_template(
        "add_task.html", message=message, jobs=jobs)


@app.route('/getresult')
def get_result():
    final_dict = dict()
    cookie_key = request.cookies.get('cookieid')
    if cookie_key == None:
        return "Enter the Url first in /add_task"
    middle_dict = r.hgetall(cookie_key)
    for keys in middle_dict.keys():
        job_id = middle_dict[keys]
        job_id = middle_dict[keys].decode()
        result_data = q.fetch_job(job_id)
        if result_data is None:
            result = None
            final_dict[keys.decode()] = result
            continue
        result = result_data.result
        final_dict[keys.decode()] = result
    return render_template("scraperesult.html", result=final_dict)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

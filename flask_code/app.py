from flask import Flask, render_template, request, make_response
import redis
from tasks import count_words
from rq import Queue
import string
import secrets
N = 16


r = redis.Redis(host='redis')
q = Queue(connection=r)
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('base.html')


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

from flask import Flask,render_template,request
import redis,time
from tasks import count_words
from rq import Queue
r= redis.Redis(host='localhost',port=6379,db=0)
q = Queue(connection=r)


final_dict = dict()
final_list = list()


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/add_task',methods = ('GET','POST'))
def add_task():
    jobs = q.jobs
    message = None
    if request.method == "POST":
        url = request.form['url']
        if url:
            task = q.enqueue(count_words,url)
            job_ids = task.key[7:]
            r.hset('key_container',url,job_ids)
            jobs = q.jobs
            q_length = len(q)
            message = f"The result is {task} and the jobs queued are {q_length}"
    return render_template("add_task.html",message= message, jobs = jobs)

@app.route('/getresult')
def get_result():
    middle_dict = r.hgetall('key_container')
    for keys in middle_dict.keys():
        job_id =middle_dict[keys]
        job_id = middle_dict[keys].decode()
        result_data = q.fetch_job(job_id)
        final_dict[keys.decode()]=result_data.result
    return render_template("scraperesult.html",result = final_dict)

if __name__ == "__main__":
    app.run(debug=True)